# LXC Docker 完整部署指南

**專案名稱：** Buddhist Education LINE Bot System  
**版本：** 2026.01  
**更新日期：** 2026-01-13

---

## 目錄

1. [環境準備](#1-環境準備)
2. [安裝 Docker](#2-安裝-docker)
3. [Clone 專案並設定](#3-clone-專案並設定)
4. [建構並啟動 Docker 服務](#4-建構並啟動-docker-服務)
5. [設定 Docker 開機自動啟動](#5-設定-docker-開機自動啟動)
6. [安裝並設定 Cloudflared](#6-安裝並設定-cloudflared)
7. [設定 Cloudflared 開機自動啟動](#7-設定-cloudflared-開機自動啟動)
8. [驗證所有服務](#8-驗證所有服務)
9. [測試重啟](#9-測試重啟)

---

## 1. 環境準備

在 Proxmox VE 上建立 LXC 容器：

```bash
# 建立 LXC
pct create 103 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.gz \
  --hostname line-bot \
  --storage zfspool \
  --rootfs zfspool:16 \
  --memory 2048 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1

# 啟動並進入容器
pct start 103
pct enter 103
```

---

## 2. 安裝 Docker

在 LXC 容器內執行：

```bash
# 更新系統
apt update && apt upgrade -y

# 使用便捷腳本安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# 啟用開機自動啟動
systemctl enable docker
systemctl start docker

# 驗證安裝
docker --version
docker compose version
```

---

## 3. Clone 專案並設定

```bash
# 進入工作目錄
cd /opt

# Clone 專案
git clone https://github.com/bbudaedu/buddhist-education-system.git

# 進入專案目錄
cd buddhist-education-system/Line-bot-llm-mysql

# 複製環境變數範例
cp .env.example .env

# 編輯環境變數
nano .env
```

### 必填環境變數

| 變數名稱 | 說明 |
|---------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot 存取權杖 |
| `LINE_CHANNEL_SECRET` | LINE Bot 密鑰 |
| `GEMINI_API_KEY` | Google Gemini API 金鑰 |
| `DB_HOST` | 資料庫主機 |
| `DB_USER` | 資料庫使用者 |
| `DB_PASSWORD` | 資料庫密碼 |
| `DB_NAME` | 資料庫名稱 |

---

## 4. 建構並啟動 Docker 服務

```bash
# 建構所有映像
docker compose build

# 啟動服務（背景運行）
docker compose up -d line-bot-web line-bot-scheduler

# 查看狀態
docker compose ps

# 查看日誌
docker compose logs -f
```

---

## 5. 設定 Docker 開機自動啟動

建立 systemd 服務：

```bash
cat > /etc/systemd/system/linebot-docker.service << 'EOF'
[Unit]
Description=LINE Bot Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/buddhist-education-system/Line-bot-llm-mysql
ExecStart=/usr/bin/docker compose up -d line-bot-web line-bot-scheduler
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

# 載入並啟用服務
systemctl daemon-reload
systemctl enable linebot-docker.service
systemctl start linebot-docker.service
```

---

## 6. 安裝並設定 Cloudflared

```bash
# 下載並安裝 cloudflared
curl -L --output cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared.deb
rm cloudflared.deb

# 登入 Cloudflare（首次設定）
cloudflared tunnel login

# 創建 tunnel（首次設定）
cloudflared tunnel create linebot-linux
```

### 設定 Tunnel 配置

```bash
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: linebot-linux
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: your-domain.com
    service: http://localhost:3000
  - service: http_status:404
EOF
```

> **注意：** 請將 `<TUNNEL_ID>` 替換為實際的 Tunnel ID，`your-domain.com` 替換為您的網域。

---

## 7. 設定 Cloudflared 開機自動啟動

```bash
cat > /etc/systemd/system/cloudflared-tunnel.service << 'EOF'
[Unit]
Description=Cloudflare Tunnel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/cloudflared tunnel run linebot-linux
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 載入並啟用服務
systemctl daemon-reload
systemctl enable cloudflared-tunnel.service
systemctl start cloudflared-tunnel.service
```

---

## 8. 驗證所有服務

```bash
# 檢查服務狀態
systemctl status linebot-docker.service
systemctl status cloudflared-tunnel.service

# 檢查 Docker 容器
docker compose ps

# 檢查健康狀態
curl http://localhost:3000/health

# 查看 Docker 日誌
docker compose logs -f

# 查看 Cloudflared 日誌
journalctl -u cloudflared-tunnel.service -f
```

---

## 9. 測試重啟

```bash
# 重啟容器
reboot

# 重啟後檢查服務
systemctl status linebot-docker.service
systemctl status cloudflared-tunnel.service
docker compose ps
```

---

## 開機啟動順序圖

```
系統啟動
    │
    ▼
docker.service (Docker 引擎)
    │
    ▼
linebot-docker.service (LINE Bot Web + Scheduler)
    │
    ▼
cloudflared-tunnel.service (Cloudflare Tunnel)
    │
    ▼
✅ 服務就緒，外部可存取
```

---

## 常用維護指令

| 功能 | 指令 |
|------|------|
| 查看容器狀態 | `docker compose ps` |
| 查看日誌 | `docker compose logs -f` |
| 重啟服務 | `docker compose restart` |
| 停止服務 | `docker compose down` |
| 更新程式碼 | `git pull && docker compose build && docker compose up -d` |
| 測試新書處理 | `docker compose run --rm ebook-processor python run_newbook_scheduler.py --check-only` |

---

**文件結束**

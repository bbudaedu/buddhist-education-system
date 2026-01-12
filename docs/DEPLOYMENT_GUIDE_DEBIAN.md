# Debian 12 遷移與部署指南 (Migration Guide)

本指南說明如何將開發完畢的 LINE Bot 系統遷移至全新的 Debian 12 伺服器上運作。

## 🛠️ 第一階段：Debian 12 伺服器準備

### 1. 系統更新與基礎套件

以 `root` 或 `sudo` 權限執行：

```bash
apt update && apt upgrade -y
apt install -y curl git unzip
```

### 2. 安裝 Docker (官方推薦方式)

不要直接用 `apt install docker.io` (版本通常較舊)，建議使用 Docker 官方腳本：

```bash
# 下載並執行官方安裝腳本
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 啟動並設定開機自啟
systemctl enable --now docker
```

*(可選) 如果您不是用 root 登入，要讓目前使用者能執行 docker 指令：*
```bash
usermod -aG docker $USER
# 登出再登入後生效
```

### 3. 安裝 Docker Compose

新版 Docker (Compose V2) 已經整合在 `docker` 指令中了。
驗證安裝：
```bash
docker compose version
# 應該會看到 Docker Compose version v2.x.x
```

---

## 📦 第二階段：專案遷移 (從 Windows 到 Debian)

假設您的專案在 Windows 的 `D:\AI Studio\newinfo`。
我們需要把以下三個資料夾傳到 Debian 主機上的 `/opt/line-bot` (或您的家目錄)：

### 需要傳送的資料夾
1. `Line-bot-llm-mysql/` (核心程式碼)
2. `ebook/` (Python 爬蟲與配置)
3. `migrations/` (資料庫初始化腳本，如果有的話)

### 傳檔方法 (推薦使用 SCP 或 SFTP)

**方法 A: 如果您有裝 WinSCP (圖形介面，最推薦)**
1. 連線到 Debian 主機。
2. 建立目錄 `/opt/line-bot`。
3. 把 Windows 上的 `Line-bot-llm-mysql`, `ebook` 整個拖拉過去。

**方法 B: 使用 PowerShell SCP 指令**
```powershell
# 在 Windows PowerShell 執行
scp -r "D:\AI Studio\newinfo\Line-bot-llm-mysql" user@debian-ip:/home/user/
scp -r "D:\AI Studio\newinfo\ebook" user@debian-ip:/home/user/
```

---

## 🚀 第三階段：啟動服務

### 1. 調整目錄結構

確保 Debian 上的目錄結構如下 (與 Windows 開發環境保持一致)：

```text
/home/user/ (或 /opt/line-bot/)
├── Line-bot-llm-mysql/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── ...
└── ebook/
    ├── run_newbook_scheduler.py
    └── ...
```

### 2. 設定環境變數

進入專案目錄：
```bash
cd Line-bot-llm-mysql
```

建立 `.env` 檔案 (您可以從 Windows 的 `.env` 複製內容過來)：
```bash
nano .env
# 貼上內容，並確認 DB_HOST=124.219.37.161 (外部資料庫 IP)
# Ctrl+O 存檔, Ctrl+X 離開
```

### 3. 啟動容器

```bash
# 建構並背景啟動
docker compose up -d --build
```

### 4. 驗證

```bash
# 查看狀態
docker compose ps

# 查看日誌
docker compose logs -f
```

如果看到 `🚀 LINE Book Query Bot server is running`，恭喜您，遷移成功！

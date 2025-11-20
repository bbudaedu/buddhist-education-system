# 管理員測試指令修復完成

## 問題描述

輸入 `flex1` 時被當作書籍查詢處理，而不是執行測試指令。

## 根本原因

1. **指令檢查順序錯誤**
   - 管理員測試指令檢查在訂閱指令之後
   - 應該優先檢查管理員測試指令

2. **異步初始化問題**
   - `adminService` 使用異步初始化
   - `isAdmin()` 方法在初始化完成前可能返回錯誤結果

## 修復內容

### 1. 調整指令檢查順序

**修改檔案：** `src/handlers/webhookHandler.ts`

```typescript
// 修復前：管理員檢查在訂閱指令之後
if (await this.handleSubscriptionCommand(...)) { return; }
if (userId && adminService.isAdmin(userId)) { ... }

// 修復後：管理員檢查優先
if (userId && await adminService.isAdmin(userId)) {
  const isTestCommand = await this.handleAdminTestCommand(...);
  if (isTestCommand) { return; }
}
if (await this.handleSubscriptionCommand(...)) { return; }
```

### 2. 修復異步初始化

**修改檔案：** `src/services/adminService.ts`

**新增：**
- `initPromise: Promise<void>` - 初始化 Promise
- `initialized: boolean` - 初始化狀態標記
- `ensureInitialized()` - 確保初始化完成

**修改：**
- `isAdmin()` 改為異步方法
- 所有方法在執行前先調用 `ensureInitialized()`

```typescript
// 修復前
isAdmin(userId: string): boolean {
  return this.adminUserIds.has(userId);
}

// 修復後
async isAdmin(userId: string): Promise<boolean> {
  await this.ensureInitialized();
  return this.adminUserIds.has(userId);
}
```

## 測試驗證

### 重新編譯
```bash
cd Line-bot-llm-mysql
npm run build
```

### 重啟伺服器
```bash
npm start
```

### 測試指令
在 LINE Bot 中輸入：
- `flex1` - 應該顯示新書通知測試
- `flex2` - 應該顯示新聞公告測試
- `flex3` - 應該顯示停課通知測試
- `flex4` - 應該顯示整合通知測試

## 預期行為

### 管理員用戶
- 輸入 `flex1-4` → 顯示測試 Flex Message
- 輸入其他文字 → 正常的書籍查詢

### 非管理員用戶
- 輸入 `flex1-4` → 當作書籍查詢處理
- 輸入其他文字 → 正常的書籍查詢

## 執行順序

```
用戶發送訊息
    ↓
檢查是否為管理員 (await adminService.isAdmin)
    ↓ (是)
檢查是否為測試指令 (flex1-4)
    ↓ (是)
發送測試 Flex Message
    ↓
結束（不繼續處理）

    ↓ (否 - 不是測試指令)
檢查是否為「最新消息」指令
    ↓
檢查是否為訂閱指令
    ↓
使用 Gemini 處理書籍查詢
```

## 相關檔案

**修改：**
- `src/handlers/webhookHandler.ts` - 調整指令檢查順序
- `src/services/adminService.ts` - 修復異步初始化

**測試：**
- 重新編譯：`npm run build`
- 重啟伺服器：`npm start`
- 在 LINE 中測試 `flex1-4` 指令

## 狀態
✅ 修復完成，已編譯成功

## 下一步
1. 重啟 Bot 伺服器
2. 在 LINE 中測試 `flex1` 指令
3. 驗證顯示 Flex Message 而不是書籍查詢結果

## 修復日期
2025-11-18

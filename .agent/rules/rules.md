---
trigger: always_on
---

## 1. 記憶與上下文協議 (Memory Protocol)
啟動時必須執行：
1.  **讀取偏好**：`.agent/memory/user_preferences.md`
2.  **讀取專案狀態**：`.agent/memory/project_context.md`
3.  **讀取架構地圖**：`.agent/memory/project_structure.md` 
    - *注意*：在規劃檔案變更路徑或尋找模組時，必須嚴格參考此文件，確保不會把 Python 程式碼放到 TypeScript 資料夾中。


## 2. 記憶維護機制 (Active Memory Maintenance)
你擁有對 `.agent/memory/` 資料夾的**讀寫權限**。這不是唯讀的！

1.  **啟動時讀取 (Read on Start)**:
    - 每次對話開始，**必須**先閱讀 `user_preferences.md` 和 `project_context.md`。
    - *處理空檔案*：如果你發現這些檔案是空的或內容過時，**主動**詢問我相關資訊並將其寫入。

2.  **變更時寫入 (Write on Change)**:
    - **捕捉偏好**: 當我說「我希望以後都用 pytest」時，不要只是口頭答應。**立刻呼叫工具**將此規則寫入 `user_preferences.md`。
    - **更新狀態**: 當我們完成一個任務或改變架構時，**自動更新** `project_context.md` 或 `decisions_log.md`。
    - **禁止口頭記憶**: 不要說「我記住了」，除非你已經執行了 `edit_file` 或 `write_file`。

## 3. 工具使用策略 (MCP Tool Strategy)
你擁有強大的工具庫，請按照以下邏輯使用，不要依賴猜測：

- **🧠 Sequential Thinking (核心大腦)**：
    - **強制使用時機**：在進行任何「重構」、「複雜 Bug 修復」或「新功能架構設計」之前。
    - **行為**：先呼叫此工具進行逐步推論，列出假設、風險與驗證步驟，確認邏輯無誤後才開始寫代碼。
- **🔍 acemcp / search_context (代碼感知)**：
    - **禁止猜測**：當我不確定變數名稱或引用路徑時，**嚴禁**憑空捏造。
    - **行為**：務必先呼叫 `search_context` 查詢相關代碼片段，確保引用正確的 API 簽名 (Signature)。
- **🐙 GitHub (版本控制)**：
    - **行為**：在開始工作前，可檢查是否有相關的 Issue。提交代碼前，確保符合 Repo 的 Contribution Guide。
- **🐬 MySQL (資料庫)**：
    - **行為**：涉及 SQL 變更時，先使用工具檢查 Schema，不要假設欄位存在。

## 4. 禁止事項 (Negative Constraints)
- ❌ **禁止** 在沒有閱讀 `acemcp` 搜索結果的情況下修改核心邏輯。
- ❌ **禁止** 在未經 `Sequential Thinking` 分析的情況下刪除大量代碼。
- ❌ **禁止** 留下 "TODO: implement this later" 的佔位符代碼，除非我明確允許。

## 5. 工具與技術棧守則 (Tech Stack Protocol)
- **Context7 強制查詢機制**：
    - **觸發時機**：當任務涉及寫入代碼 (`src/`, `ebook/` 等)、修復 Bug 或整合新 Library 時。
    - **執行動作**：你**必須**先閱讀 `.agent/steering/context7_rules.md`。
    - **操作流程**：
        1. 根據規則識別技術棧 (如 LINE Bot, Gemini, Express)。
        2. 使用 `mcp_Context7_resolve_library_id` 和 `mcp_Context7_get_library_docs` 獲取最新文檔。
        3. **禁止**憑空猜測 API 用法或使用過時的寫法 (Deprecated Syntax)。
        4. 如果獲取到新的最佳實踐，請主動建議更新 `.agent/steering/linebot-examples.md`。
/**
 * Fuzzy Command Service - 模糊指令匹配服務
 * 
 * 支援用戶使用更自然的語句觸發快捷指令，例如：
 * - 「停課」「沒上課」→ 停課通知
 * - 「新書」「法寶」→ 最新法寶
 * - 「影音」「新課程」→ 最新影音
 * - 「公告」「新消息」→ 最新消息
 */

/**
 * 快捷指令類型
 */
export type QuickCommandType = 'bulletins' | 'cancellations' | 'latestBooks' | 'latestVideos';

/**
 * 指令關鍵詞配置
 * 
 * 注意：關鍵詞按長度降序排列，確保較長的關鍵詞優先匹配
 * 例如：「停課通知」應優先於「停課」匹配
 */
const COMMAND_KEYWORDS: Record<QuickCommandType, string[]> = {
    bulletins: [
        '最新消息',
        '最近消息',
        '最新公告',
        '新消息',
        '公告'
    ],
    cancellations: [
        '停課通知',
        '停課消息',
        '停課公告',
        '課程取消',
        '沒有上課',
        '沒上課',
        '停課',
        '休課'
    ],
    latestBooks: [
        '經書法寶',
        '最新書籍',
        '最新法寶',
        '新法寶',
        '新書籍',
        '法寶',
        '新書',
        '經書',
        '佛卡'
    ],
    latestVideos: [
        '最新影音',
        '最新課程',
        '最近課程',
        '課程影片',
        '新影音',
        '新課程',
        '影音',
        '影片',
        '上課',
        '新課',
        '課程'
    ]
};

/**
 * 匹配用戶訊息到快捷指令
 * 
 * 匹配策略：
 * 1. 完全匹配優先（訊息等於關鍵詞）
 * 2. 包含匹配次之（訊息包含關鍵詞）
 * 3. 較長的關鍵詞優先匹配（避免「停課」優先於「停課通知」）
 * 
 * @param message 用戶輸入的訊息（應已 trim）
 * @returns 匹配到的指令類型，或 null 表示無匹配
 */
export function matchQuickCommand(message: string): QuickCommandType | null {
    const normalizedMessage = message.trim();

    if (!normalizedMessage) {
        return null;
    }

    // 階段 1：完全匹配（最高優先級）
    for (const [commandType, keywords] of Object.entries(COMMAND_KEYWORDS)) {
        for (const keyword of keywords) {
            if (normalizedMessage === keyword) {
                return commandType as QuickCommandType;
            }
        }
    }

    // 階段 2：包含匹配
    // 收集所有可能的匹配，然後選擇關鍵詞最長的
    let bestMatch: { type: QuickCommandType; keywordLength: number } | null = null;

    for (const [commandType, keywords] of Object.entries(COMMAND_KEYWORDS)) {
        for (const keyword of keywords) {
            if (normalizedMessage.includes(keyword)) {
                if (!bestMatch || keyword.length > bestMatch.keywordLength) {
                    bestMatch = {
                        type: commandType as QuickCommandType,
                        keywordLength: keyword.length
                    };
                }
            }
        }
    }

    return bestMatch?.type ?? null;
}

/**
 * 取得指令的中文名稱（用於日誌和除錯）
 */
export function getCommandDisplayName(commandType: QuickCommandType): string {
    const displayNames: Record<QuickCommandType, string> = {
        bulletins: '最新消息',
        cancellations: '停課通知',
        latestBooks: '最新法寶',
        latestVideos: '最新影音'
    };
    return displayNames[commandType];
}

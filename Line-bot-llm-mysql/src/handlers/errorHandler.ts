/**
 * 錯誤處理模組
 * 提供統一的錯誤處理和日誌記錄功能
 */

export enum ErrorType {
  GEMINI_API_ERROR = 'GEMINI_API_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  LINE_API_ERROR = 'LINE_API_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export interface ErrorContext {
  userId?: string | undefined;
  userMessage?: string;
  operation: string;
}

/**
 * 錯誤類型與友善訊息的對應表
 */
const errorMessages: Record<ErrorType, string> = {
  [ErrorType.GEMINI_API_ERROR]: '抱歉，AI 助理暫時無法回應，請稍後再試。',
  [ErrorType.DATABASE_ERROR]: '書庫系統維護中，請稍後再試。',
  [ErrorType.LINE_API_ERROR]: '訊息發送失敗，請重新傳送您的問題。',
  [ErrorType.VALIDATION_ERROR]: '您的訊息格式有誤，請重新輸入。',
  [ErrorType.UNKNOWN_ERROR]: '系統發生錯誤，我們正在處理中。'
};

/**
 * 根據錯誤類型分類錯誤
 */
function classifyError(error: Error): ErrorType {
  const errorMessage = error.message.toLowerCase();
  
  // 優先檢查資料庫相關錯誤
  if (errorMessage.includes('database') || errorMessage.includes('mysql') || errorMessage.includes('connection')) {
    return ErrorType.DATABASE_ERROR;
  }
  
  // 檢查 LINE API 相關錯誤
  if (errorMessage.includes('line') || errorMessage.includes('messaging') || errorMessage.includes('reply')) {
    return ErrorType.LINE_API_ERROR;
  }
  
  // 檢查驗證相關錯誤
  if (errorMessage.includes('validation') || errorMessage.includes('invalid')) {
    return ErrorType.VALIDATION_ERROR;
  }
  
  // 檢查 Gemini AI 相關錯誤
  if (errorMessage.includes('gemini') || errorMessage.includes('ai') || errorMessage.includes('generative')) {
    return ErrorType.GEMINI_API_ERROR;
  }
  
  return ErrorType.UNKNOWN_ERROR;
}

/**
 * 記錄錯誤資訊（不包含敏感資料）
 */
export function logError(error: Error, context: ErrorContext): void {
  const timestamp = new Date().toISOString();
  const errorType = classifyError(error);
  
  // 建立安全的日誌物件，移除敏感資訊
  const logData = {
    timestamp,
    errorType,
    operation: context.operation,
    errorMessage: error.message,
    errorStack: error.stack,
    // 只記錄用戶ID的前幾位，保護隱私
    userId: context.userId ? `${context.userId.substring(0, 8)}...` : undefined,
    // 不記錄完整的用戶訊息，只記錄長度
    userMessageLength: context.userMessage?.length
  };
  
  console.error('Error occurred:', JSON.stringify(logData, null, 2));
}

/**
 * 處理錯誤並回傳友善的用戶訊息
 */
export function handleError(error: Error, context: ErrorContext): string {
  // 記錄錯誤
  logError(error, context);
  
  // 分類錯誤並回傳對應的友善訊息
  const errorType = classifyError(error);
  return errorMessages[errorType];
}

/**
 * 錯誤處理類別，提供更結構化的錯誤處理
 */
export class ErrorHandler {
  /**
   * 處理錯誤並回傳友善訊息
   */
  static handle(error: Error, context: ErrorContext): string {
    return handleError(error, context);
  }
  
  /**
   * 記錄錯誤
   */
  static log(error: Error, context: ErrorContext): void {
    logError(error, context);
  }
  
  /**
   * 分類錯誤類型
   */
  static classify(error: Error): ErrorType {
    return classifyError(error);
  }
  
  /**
   * 取得友善錯誤訊息
   */
  static getFriendlyMessage(errorType: ErrorType): string {
    return errorMessages[errorType];
  }
}
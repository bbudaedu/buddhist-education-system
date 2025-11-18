/**
 * Book interface representing the structure of book records in the database
 */
export interface Book {
  /** 書籍唯一識別碼 */
  book_id: string;
  
  /** 書名 */
  title: string;
  
  /** 作者 */
  author?: string;
  
  /** 目前的庫存數量 */
  quantity: number;
  
  /** 存放位置或書架號 */
  shelf_location: string;
  
  /** 所在的分館或館藏地 */
  library_branch: string;
}
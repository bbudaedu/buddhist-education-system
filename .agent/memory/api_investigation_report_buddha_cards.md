# 佛卡 API 調查報告

## 1. 列表 API
- **URL**: `https://publish.budaedu.org/dharma/public/api/pictures`
- **Method**: GET
- **Response Format**: JSON Array
- **Sample Item**:
  ```json
  {
      "id": "8",
      "code": "BP019",
      "chinese_name": "南傳本師佛像 大張(斯里蘭卡版)-海報",
      "chinese_spec": "43.5*62CM/海報",
      "updated_at": "2025-05-21 16:21:00",
      "type_name": ""
  }
  ```

## 2. 單張圖片詳情 API (參考)
- **URL**: `https://publish.budaedu.org/dharma/public/api/pictures/{id}/downloadable-efile`
- **Response**:
  ```json
  {
      "data": {
          "id": "11006",
          "name": "BP394.jpg",
          "url": "https://www2.budaedu.org/dharma-data/picture-downloadable-efile/BP394.jpg"
      }
  }
  ```

## 3. 圖片 URL 規則推導
根據單張圖片詳情與列表數據的對應關係：
- 列表中的 `code` (如 `BP019`) 對應圖片文件名。
- **推測 URL 模式**: `https://www2.budaedu.org/dharma-data/picture-downloadable-efile/{code}.jpg`

## 4. 實作策略
1. 調用列表 API 獲取所有佛卡。
2. 根據 `updated_at` 降序排序。
3. 取前 5 筆。
4. 使用 `code` 字段構造圖片 URL。

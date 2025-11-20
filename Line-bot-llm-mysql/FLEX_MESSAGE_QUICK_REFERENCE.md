# Flex Message 快速參考

## 創建新書 Carousel

```typescript
import { flexMessageService } from './src/services/flexMessageService';

const books = [
  {
    title: '金剛經講記',
    author: '淨空法師',
    pdfUrls: [
      'https://example.com/book1.pdf',
      'https://example.com/book1-part2.pdf'
    ]
  }
];

const message = flexMessageService.createNewBooksCarousel(books);
```

## 創建新聞 Carousel

```typescript
const news = [
  {
    title: '課程公告',
    date: '2025-11-13',
    url: 'https://example.com/news/123',
    content: '課程內容說明...'
  }
];

const message = flexMessageService.createNewsCarousel(news);
```

## 創建停課通知 Carousel

```typescript
const cancellations = [
  {
    courseName: '華嚴經宗通',
    date: '2025-11-20',
    instructor: '某某法師',
    location: '七樓教室'
  }
];

const message = flexMessageService.createCancellationCarousel(cancellations);
```

## 創建整合通知

```typescript
const message = flexMessageService.createIntegratedNotification({
  newBooks: [...],
  news: [...],
  cancellations: [...]
});
```

## Python 端發送

```python
# 準備結構化資料
structured_data = {
    'newBooks': [
        {
            'title': '書名',
            'author': '作者',
            'pdfUrls': ['url1', 'url2']
        }
    ],
    'news': [
        {
            'title': '標題',
            'date': '日期',
            'url': '連結',
            'content': '內容'
        }
    ],
    'cancellations': [
        {
            'courseName': '課程',
            'date': '日期',
            'instructor': '講師',
            'location': '地點'
        }
    ]
}

# 發送
line_service.send_integrated_notification(structured_data)
```

## 重要提醒

1. PDF 連結會自動加上 `?openExternalBrowser=1`
2. 最多支援 3 個 PDF 按鈕
3. 整合通知會根據用戶訂閱類型過濾
4. 單一類型訂閱使用專用 Carousel
5. 多種類型訂閱使用整合 Carousel

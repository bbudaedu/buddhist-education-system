import mysql.connector
import json

# Scraper 抓到的資料
scraped_books = [
    {
        "title": "菩提道次第廣論 CH550-03",
        "author": "宗喀巴大師 著",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_菩提道次第廣論",
        "publish_date": "2024-11-24"
    },
    {
        "title": "成唯識論研習(內地流通版) CH549-13",
        "author": "普行法師 編著",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_成唯識論研習",
        "publish_date": "2024-11-23"
    },
    {
        "title": "顯揚聖教論 CH541-10",
        "author": "無著菩薩造 唐三藏法師玄奘奉詔譯",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_顯揚聖教論",
        "publish_date": "2024-11-22"
    },
    {
        "title": "大佛頂首楞嚴經正脈疏-上、下冊（2013年10月修訂版） CH382-16",
       "author": "明 交光真鑑 述",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_大佛頂首楞嚴經正脈疏",
        "publish_date": "2024-11-21"
    },
    {
        "title": "淨土要義 CH861-40",
        "author": "懺雲老和尚開示",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_淨土要義",
        "publish_date": "2024-11-20"
    },
    {
        "title": "大手印五支道本尊修持 CH848-04",
        "author": "森給滇真仁波切　講授\\林生茂譯師　口譯",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_大手印五支道本尊修持",
        "publish_date": "2024-11-19"
    },
    {
        "title": "天台四教儀註彙補輔宏記 CH820-25",
        "author": "未知作者",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_天台四教儀註彙補輔宏記",
        "publish_date": "2024-11-18"
    },
    {
        "title": "肇論新疏 CH820-14",
        "author": "元沙門 文才 述",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_肇論新疏",
        "publish_date": "2024-11-17"
    },
    {
        "title": "楞嚴經修學法要 CH382-23",
        "author": "淨界法師 講述審閱妙法蓮心學院 編製",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_楞嚴經修學法要",
        "publish_date": "2024-11-16"
    },
    {
        "title": "六百卷大般若經經脈指引 CH327-04",
        "author": "楊宗翰 編著",
        "cover_image_url": "",
        "pdf_url": "",
        "url": "book_六百卷大般若經經脈指引",
        "publish_date": "2024-11-15"
    }
]

# 連接資料庫
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your_password',  # 請替換為實際密碼
    database='library_db'
)

cursor = conn.cursor()

# 插入資料
inserted = 0
updated = 0

for book in scraped_books:
    # 檢查是否已存在
    cursor.execute("SELECT id FROM dharma_books WHERE title = %s LIMIT 1", (book['title'],))
    existing = cursor.fetchone()
    
    if existing:
        # 更新
        cursor.execute("""
            UPDATE dharma_books 
            SET author = %s, cover_image_url = %s, pdf_url = %s, publish_date = %s
            WHERE title = %s
        """, (book['author'], book['cover_image_url'], book['pdf_url'], book['publish_date'], book['title']))
        updated += 1
    else:
        # 插入
        cursor.execute("""
            INSERT INTO dharma_books (title, author, cover_image_url, pdf_url, url, publish_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (book['title'], book['author'], book['cover_image_url'], book['pdf_url'], book['url'], book['publish_date']))
        inserted += 1

conn.commit()

print(f"✅ Sync complete: {inserted} inserted, {updated} updated")

# 查詢結果
cursor.execute("SELECT id, title, author FROM dharma_books ORDER BY publish_date DESC LIMIT 10")
books = cursor.fetchall()

print("\n📚 Latest books in database:")
for book in books:
    print(f"  {book[0]}: {book[1]} / {book[2]}")

cursor.close()
conn.close()

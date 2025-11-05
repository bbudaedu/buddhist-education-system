// Simple integration test for the daily scheduler service
const fs = require('fs').promises;
const path = require('path');

async function testIntegration() {
  console.log('🧪 Testing daily scheduler integration...');
  
  try {
    // Create a test JSON file to simulate Python processor output
    const testData = {
      processingDate: new Date().toISOString(),
      totalBooksFound: 2,
      successfullyProcessed: [
        {
          title: '測試書籍 1',
          author: '測試作者',
          summary: '這是一本測試書籍的摘要內容。',
          downloadUrl: 'https://example.com/book1.pdf',
          processingMethod: 'pdf_extract',
          processingSuccess: true,
          filename: 'test_book_1.pdf'
        },
        {
          title: '測試書籍 2',
          summary: '這是第二本測試書籍的摘要。',
          downloadUrl: 'https://example.com/book2.pdf',
          processingMethod: 'google_search',
          processingSuccess: true,
          filename: 'test_book_2.pdf'
        }
      ],
      processingStats: {
        booksProcessed: 2,
        booksFailed: 0,
        pdfExtractions: 1,
        googleSearches: 1,
        processingTimeSeconds: 120.5
      }
    };

    // Create test output directory
    const outputDir = path.join(__dirname, '..', 'ebook', 'generated_documents');
    await fs.mkdir(outputDir, { recursive: true });

    // Write test file
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const testFilePath = path.join(outputDir, `processed_books_${timestamp}.json`);
    
    await fs.writeFile(testFilePath, JSON.stringify(testData, null, 2), 'utf-8');
    
    console.log(`✅ Test file created: ${testFilePath}`);
    console.log('📁 File should be detected by the monitoring service when the server is running');
    console.log('🚀 Start the server with: npm run dev');
    console.log('📊 Check status at: http://localhost:3000/admin/scheduler');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testIntegration();
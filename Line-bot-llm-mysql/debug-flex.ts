import { flexMessageService } from './src/services/flexMessageService';

const mockBooks = [
    {
        title: '測試書籍 1',
        author: '測試作者 1',
        publishDate: '2025-11-27',
        coverImageUrl: 'https://www.budaedu.org/img/logo.png',
        pdfUrl: undefined
    },
    {
        title: '測試書籍 2',
        author: '測試作者 2',
        publishDate: '2025-11-26',
        coverImageUrl: 'https://www.budaedu.org/img/logo.png',
        pdfUrl: 'https://example.com/book2.pdf'
    }
];

try {
    console.log('Generating Flex Message...');
    const flexMessage = flexMessageService.createDharmaBookCarousel(mockBooks);
    console.log(JSON.stringify(flexMessage, null, 2));
} catch (error) {
    console.error('Error generating flex message:', error);
}

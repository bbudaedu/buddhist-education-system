import { dharmaBookService } from '../services/dharmaBookService';
import { videoSeriesService } from '../services/videoSeriesService';
import { videoStreamingService } from '../services/videoStreamingService';

async function verifyBudaeduConnector() {
    console.log('Starting BudaeduConnector Verification...');

    try {
        // 1. Test DharmaBookService
        console.log('\n--- Testing DharmaBookService ---');
        console.log('Fetching latest books...');
        const books = await dharmaBookService.getLatestBooks(5);
        console.log(`Fetched ${books.length} books.`);
        if (books.length > 0) {
            console.log('First book sample:', JSON.stringify(books[0], null, 2));
        } else {
            console.warn('No books found.');
        }

        // 2. Test VideoSeriesService
        console.log('\n--- Testing VideoSeriesService ---');
        console.log('Fetching video series...');
        const series = await videoSeriesService.getLatestSeries(5);
        console.log(`Fetched ${series.length} video series.`);
        if (series.length > 0) {
            console.log('First series sample:', JSON.stringify(series[0], null, 2));
        } else {
            console.warn('No video series found.');
        }

        // 3. Test VideoStreamingService
        console.log('\n--- Testing VideoStreamingService ---');
        console.log('Fetching live events...');
        // Note: fetchLiveEvents is private, so we test via getLatestContent
        const content = await videoStreamingService.getLatestContent(5);
        const liveEvents = content.filter(c => c.type === 'live');
        console.log(`Fetched ${liveEvents.length} live events (via getLatestContent).`);
        if (liveEvents.length > 0) {
            console.log('First live event sample:', JSON.stringify(liveEvents[0], null, 2));
        } else {
            console.log('No live events found (normal if no stream is live).');
        }

        console.log('\nVerification Completed Successfully.');
    } catch (error) {
        console.error('Verification Failed:', error);
        process.exit(1);
    }
}

verifyBudaeduConnector();

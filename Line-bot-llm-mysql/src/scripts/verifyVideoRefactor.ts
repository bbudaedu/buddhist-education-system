import { videoSeriesService } from '../services/videoSeriesService';
import { videoStreamingService } from '../services/videoStreamingService';

async function verifyVideoServices() {
    console.log('Starting Video Services Verification...');

    try {
        // 1. Test VideoSeriesService
        console.log('\n--- Testing VideoSeriesService ---');
        console.log('Fetching video series...');
        const series = await videoSeriesService.getLatestSeries();
        console.log(`Fetched ${series.length} video series.`);

        if (series.length > 0) {
            console.log('First series sample:', JSON.stringify(series[0], null, 2));
        } else {
            console.warn('No video series found. This might be expected if the API returns empty, but check if it works.');
        }

        // 2. Test VideoStreamingService (Combined Content)
        console.log('\n--- Testing VideoStreamingService (Combined Content) ---');
        console.log('Fetching all video content (limit 20)...');
        const allContent = await videoStreamingService.getLatestContent(20);
        console.log(`Fetched ${allContent.length} total video items.`);

        const seriesInContent = allContent.filter(c => c.type === 'video');
        const liveInContent = allContent.filter(c => c.type === 'live');

        console.log(`- Series: ${seriesInContent.length}`);
        console.log(`- Live: ${liveInContent.length}`);

        if (seriesInContent.length === 0 && series.length > 0) {
            console.warn('Warning: No series found in combined content even with limit 20. Live events might be dominating.');
        } else {
            console.log('Series found in combined content as expected.');
        }

        console.log('\nVerification Completed Successfully.');
    } catch (error) {
        console.error('Verification Failed:', error);
        process.exit(1);
    }
}

verifyVideoServices();

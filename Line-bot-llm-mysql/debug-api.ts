import axios from 'axios';
import https from 'https';

async function testApis() {
    console.log('Starting API tests (with SSL bypass)...');

    const axiosInstance = axios.create({
        httpsAgent: new https.Agent({
            rejectUnauthorized: false
        }),
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        timeout: 10000
    });

    // 1. Test Books API
    console.log('\n--- Testing Books API ---');
    try {
        const booksUrl = 'https://publish.budaedu.org/dharma/public/api/books/chinese';
        console.log(`URL: ${booksUrl}`);
        const booksResponse = await axiosInstance.get(booksUrl, {
            params: {
                per_page: 5,
                page: 1,
                order: 'latest_storage_date,desc'
            }
        });
        console.log(`Status: ${booksResponse.status}`);
        // console.log('Response:', JSON.stringify(booksResponse.data).substring(0, 500));

        let data = booksResponse.data;
        if (data.data) {
            console.log('Data structure: { data: [...] }');
            console.log('Count:', data.data.length);
            if (data.data.length > 0) {
                console.log('First item:', JSON.stringify(data.data[0], null, 2));
            }
        } else if (Array.isArray(data)) {
            console.log('Data structure: [...]');
            console.log('Count:', data.length);
            if (data.length > 0) {
                console.log('First item:', JSON.stringify(data[0], null, 2));
            }
        } else {
            console.log('Unknown data structure:', JSON.stringify(data).substring(0, 200));
        }

    } catch (error: any) {
        console.error('Books API Error:', error.message);
        if (error.response) {
            console.error('Response data:', error.response.data);
        }
    }

    // 2. Test Live Events API
    console.log('\n--- Testing Live Events API ---');
    try {
        const liveUrl = 'https://publish.budaedu.org/laravel/public/api/courses';
        console.log(`URL: ${liveUrl}`);
        const day = new Date().getDay();
        const weekday = day === 0 ? 7 : day;
        const liveResponse = await axiosInstance.get(liveUrl, {
            params: {
                'filter[week]': weekday,
                'filter[have_live_stream]': 'true',
                'include': 'places'
            }
        });
        console.log(`Status: ${liveResponse.status}`);

        let data = liveResponse.data;
        if (Array.isArray(data)) {
            console.log('Count:', data.length);
            if (data.length > 0) {
                console.log('First item:', JSON.stringify(data[0], null, 2));
            }
        } else if (data && data.data) {
            console.log('Data structure: { data: [...] }');
            console.log('Count:', data.data.length);
        } else {
            console.log('Unknown data structure:', JSON.stringify(data).substring(0, 200));
        }
    } catch (error: any) {
        console.error('Live Events API Error:', error.message);
    }

    // 3. Test Video Series API
    console.log('\n--- Testing Video Series API ---');
    try {
        const seriesUrl = 'https://publish.budaedu.org/audiovisual/public/api/series/by-keyword-searched';
        console.log(`URL: ${seriesUrl}`);
        const seriesResponse = await axiosInstance.get(seriesUrl, {
            params: {
                'filter[ended]': 'N',
                'order': 'latest_filedate,desc',
                'per_page': 5
            }
        });
        console.log(`Status: ${seriesResponse.status}`);

        let data = seriesResponse.data;
        if (Array.isArray(data)) {
            console.log('Count:', data.length);
            if (data.length > 0) {
                console.log('First item:', JSON.stringify(data[0], null, 2));
            }
        } else if (data && data.data) {
            console.log('Data structure: { data: [...] }');
            console.log('Count:', data.data.length);
        } else {
            console.log('Unknown data structure:', JSON.stringify(data).substring(0, 200));
        }
    } catch (error: any) {
        console.error('Video Series API Error:', error.message);
    }
}

testApis();

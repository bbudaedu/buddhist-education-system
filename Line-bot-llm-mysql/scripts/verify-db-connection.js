require('dotenv').config({ path: '../.env' }); // Adjust path if running from scripts/
const mysql = require('mysql2/promise');

async function verifyConnection() {
    console.log('🔍 Testing database connection...');
    console.log(`📡 Host: ${process.env.DB_HOST}`);
    console.log(`👤 User: ${process.env.DB_USER}`);
    console.log(`🗄️  Database: ${process.env.DB_NAME}`);

    try {
        const connection = await mysql.createConnection({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME,
            port: process.env.DB_PORT || 3306,
            connectTimeout: 5000
        });

        console.log('✅ Connection successful!');

        // Simple query test
        const [rows] = await connection.execute('SELECT 1 as val');
        console.log('✅ Query test passed:', rows[0].val === 1 ? 'OK' : 'Fail');

        await connection.end();
        process.exit(0);
    } catch (err) {
        console.error('❌ Connection failed:');
        console.error(`   Error: ${err.message}`);
        console.error(`   Code: ${err.code}`);
        if (err.code === 'ETIMEDOUT') {
            console.error('   Hint: Check if the IP is correct and firewall allows connection to port 3306.');
        } else if (err.code === 'ER_ACCESS_DENIED_ERROR') {
            console.error('   Hint: Check username/password and user permissions for this host.');
        }
        process.exit(1);
    }
}

verifyConnection();

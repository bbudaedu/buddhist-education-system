const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

// Load config from environment or hardcoded defaults (matching the project)
// In a real scenario we would parse .env or config.ts, but for this script we'll try to be robust
const config = {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'password',
    database: process.env.DB_NAME || 'library_db'
};

async function verify() {
    console.log(`Connecting to ${config.host} as ${config.user}...`);
    let connection;
    try {
        connection = await mysql.createConnection(config);

        // Check dharma_books table
        const [tables] = await connection.execute("SHOW TABLES LIKE 'dharma_books'");
        if (tables.length > 0) {
            console.log("SUCCESS: Table 'dharma_books' exists.");
        } else {
            console.log("FAILURE: Table 'dharma_books' does NOT exist.");

            // Try to run the migration SQL directly if it fails
            console.log("Attempting to run migration SQL...");
            const sqlPath = path.join(__dirname, '../Line-bot-llm-mysql/migrations/002_add_dharma_books_and_videos.sql');
            if (fs.existsSync(sqlPath)) {
                const sql = fs.readFileSync(sqlPath, 'utf8');
                const statements = sql.split(';').filter(s => s.trim());
                for (const stmt of statements) {
                    if (stmt.trim()) {
                        try {
                            await connection.execute(stmt);
                            console.log("Executed SQL statement.");
                        } catch (err) {
                            console.log(`Error executing statement: ${err.message}`);
                        }
                    }
                }
                console.log("Migration SQL execution completed.");
            } else {
                console.log(`Migration file not found at ${sqlPath}`);
            }
        }

        // Check subscribers table
        const [columns] = await connection.execute("SHOW COLUMNS FROM subscribers LIKE 'subscribed_videos'");
        if (columns.length > 0) {
            console.log("SUCCESS: Column 'subscribed_videos' exists in 'subscribers'.");
        } else {
            console.log("FAILURE: Column 'subscribed_videos' does NOT exist in 'subscribers'.");
        }

    } catch (err) {
        console.error("Error:", err.message);
    } finally {
        if (connection) await connection.end();
    }
}

verify();

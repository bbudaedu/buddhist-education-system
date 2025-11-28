import { databaseService } from './src/services/databaseService';
import * as fs from 'fs';
import * as path from 'path';

async function runMigration() {
    try {
        console.log('🔄 Running migration: 002_add_dharma_books_and_videos.sql...');

        const migrationPath = path.join(__dirname, 'migrations', '002_add_dharma_books_and_videos.sql');
        const sql = fs.readFileSync(migrationPath, 'utf-8');

        // Split by semicolon and execute each statement
        const statements = sql
            .split(';')
            .map(s => s.trim())
            .filter(s => s.length > 0 && !s.startsWith('--'));

        for (const statement of statements) {
            if (statement.trim()) {
                console.log(`Executing: ${statement.substring(0, 50)}...`);
                await (databaseService as any).pool.execute(statement);
            }
        }

        console.log('✅ Migration completed successfully!');

        // Verify table creation
        const [tables] = await (databaseService as any).pool.execute(
            "SHOW TABLES LIKE 'dharma_books'"
        );
        console.log('📊 Verification:', tables);

        process.exit(0);
    } catch (error) {
        console.error('❌ Migration failed:', error);
        process.exit(1);
    }
}

runMigration();

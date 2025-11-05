# Database Migrations

This directory contains SQL migration files for the LINE Book Query Bot database schema.

## Migration Files

- `001_create_user_subscriptions.sql` - Creates the user_subscriptions table for managing daily notification subscriptions
- `002_create_notification_logs.sql` - Creates the notification_logs table for tracking daily processing statistics
- `003_create_delivery_failures.sql` - Creates the delivery_failures table for tracking failed notification deliveries

## Running Migrations

To run all pending migrations:

```bash
npm run migrate
```

This will:
1. Create a `migrations` table to track executed migrations
2. Execute any SQL files that haven't been run yet
3. Record successful migrations to prevent re-execution

## Migration File Format

Migration files should:
- Be named with a numeric prefix (001_, 002_, etc.)
- End with `.sql` extension
- Contain valid SQL statements
- Use `CREATE TABLE IF NOT EXISTS` for safety
- Include appropriate indexes for performance

## Database Schema

After running migrations, the following tables will be created:

### user_subscriptions
Stores user subscription preferences for daily book notifications.

### notification_logs
Tracks daily notification processing statistics and performance metrics.

### delivery_failures
Records failed notification delivery attempts for debugging and retry logic.

## Development

When adding new migrations:
1. Create a new SQL file with the next sequential number
2. Test the migration on a development database
3. Ensure the migration is idempotent (safe to run multiple times)
4. Update this README if needed
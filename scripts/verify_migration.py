import mysql.connector
import json
import os

def load_config():
    # Try to load from Line-bot-llm-mysql/src/config.ts (parsing TS file is hard, let's try to find a json config or use env vars if available)
    # Or better, use the config from ebook/config.json if it has DB creds?
    # ebook/config.json usually has API URL.
    # Let's try to read from .env file in Line-bot-llm-mysql if it exists.
    
    env_path = os.path.join('Line-bot-llm-mysql', '.env')
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

def verify_migration():
    config = load_config()
    
    # Fallback to default credentials if not found in .env (assuming local dev defaults)
    host = config.get('DB_HOST', 'localhost')
    user = config.get('DB_USER', 'root')
    password = config.get('DB_PASSWORD', 'password') # Replace with actual default if known, or try empty
    database = config.get('DB_NAME', 'library_db')
    
    print(f"Connecting to {host} as {user}...")
    
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Check dharma_books table
        cursor.execute("SHOW TABLES LIKE 'dharma_books'")
        result = cursor.fetchone()
        if result:
            print("SUCCESS: Table 'dharma_books' exists.")
        else:
            print("FAILURE: Table 'dharma_books' does NOT exist.")
            
        # Check subscribers table for subscribed_videos column
        cursor.execute("SHOW COLUMNS FROM subscribers LIKE 'subscribed_videos'")
        result = cursor.fetchone()
        if result:
            print("SUCCESS: Column 'subscribed_videos' exists in 'subscribers'.")
        else:
            print("FAILURE: Column 'subscribed_videos' does NOT exist in 'subscribers'.")
            
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    verify_migration()

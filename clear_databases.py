import os
import sqlite3
import time

def clear_database(db_path):
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Connect to the database with timeout
            conn = sqlite3.connect(db_path, timeout=20)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Delete all data from each table
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # Skip sqlite_sequence table
                    try:
                        cursor.execute(f"DELETE FROM {table_name};")
                        print(f"Cleared data from {table_name} in {os.path.basename(db_path)}")
                    except sqlite3.Error as e:
                        print(f"Error clearing table {table_name}: {str(e)}")
            
            # Reset auto-increment counters if the table exists
            try:
                cursor.execute("DELETE FROM sqlite_sequence;")
            except sqlite3.Error:
                pass  # Ignore if sqlite_sequence doesn't exist
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            print(f"Successfully cleared {os.path.basename(db_path)}")
            return True
            
        except sqlite3.Error as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to clear {db_path} after {max_retries} attempts")
                return False

def main():
    # Get the instance directory path
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    
    # List of database files to clear
    db_files = ['students.db', 'lectures.db', 'attendance.db']
    
    # Clear each database
    for db_file in db_files:
        db_path = os.path.join(instance_dir, db_file)
        if os.path.exists(db_path):
            print(f"\nAttempting to clear {db_file}...")
            if clear_database(db_path):
                print(f"Successfully cleared {db_file}")
            else:
                print(f"Failed to clear {db_file}")
        else:
            print(f"Database file not found: {db_path}")

if __name__ == "__main__":
    main() 
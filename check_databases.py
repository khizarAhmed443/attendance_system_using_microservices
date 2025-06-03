import os
import sqlite3

def check_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\nChecking {os.path.basename(db_path)}:")
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"Table {table_name}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking {db_path}: {str(e)}")

def main():
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    db_files = ['students.db', 'lectures.db', 'attendance.db']
    
    for db_file in db_files:
        db_path = os.path.join(instance_dir, db_file)
        if os.path.exists(db_path):
            check_database(db_path)
        else:
            print(f"\nDatabase file not found: {db_path}")

if __name__ == "__main__":
    main() 
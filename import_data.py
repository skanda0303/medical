import json
import psycopg2
from psycopg2 import extras
import os
import glob # Used for finding all files matching a pattern

# --- Configuration (UPDATE THESE) ---
DB_NAME = "database1"
DB_USER = "postgres"
DB_PASS = "skanda" # Assuming this is your confirmed password
HOST = "localhost"
PORT = "5432"
DATA_DIR = r"C:\Users\night\OneDrive\Desktop\postgre\DB_Dataset\DB_Dataset\data" 

# --- Helper Function for Data Conversion ---
def safe_value(value):
    """Converts complex Python types (dict/list) into JSON strings for PostgreSQL."""
    if isinstance(value, dict) or isinstance(value, list):
        # Convert the dictionary or list into a valid JSON string
        return json.dumps(value)
    
    # Optional: You can add logic here to convert empty strings '' to None for numeric fields
    if value == '': 
         return None
         
    return value

# --- Database Connection Function ---
def connect_db():
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=HOST, port=PORT
    )
    return conn

# --- Main Import Function (MODIFIED) ---
def import_data():
    conn = None
    all_data = []
    
    # Step 1: Aggregate Data
    # ... [Aggregation logic remains the same] ...
    
    print(f"Searching for JSON files in: {DATA_DIR}...")
    json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    
    if not json_files:
        print("Error: No JSON files found in the data directory. Check your DATA_DIR path.")
        return

    print(f"Found {len(json_files)} files. Aggregating data...")

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                all_data.extend(file_data)
        except Exception as e:
            print(f"Warning: Could not read or parse file {file_path}. Error: {e}")

    if not all_data:
        print("Error: No medicine data was successfully loaded.")
        return
        
    # --- Step 2: Connect and Insert Data ---
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Safely determine columns from the first record
        # Note: You MUST ensure your medicines table in PostgreSQL has columns 
        # matching ALL the keys found here, including any new JSONB columns you added!
        columns = all_data[0].keys()
        table_name = "medicines"
        
        # Prepare the SQL command
        columns_list = ', '.join(columns)
       # Tells PostgreSQL: if an ID already exists, just ignore the new record and continue.
        insert_query = f"INSERT INTO {table_name} ({columns_list}) VALUES %s ON CONFLICT (id) DO NOTHING"
        
        # ***************************************************************
        # *** CRITICAL CHANGE: Use safe_value to handle dictionary types **
        # ***************************************************************
        values = [[safe_value(item.get(col)) for col in columns] for item in all_data]
        
        print(f"Inserting {len(all_data)} total records into '{table_name}'...")
        
        # Use execute_values for fast bulk insertion
        extras.execute_values(cursor, insert_query, values, page_size=1000) 
        
        conn.commit()
        print("Data import successful!")

    except Exception as e:
        print(f"An error occurred during DB operation: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import_data()
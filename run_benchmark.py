

import json
import requests
import time

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/search"
BENCHMARK_FILE = r"DB_Dataset\DB_Dataset\benchmark_queries.json"
SUBMISSION_FILE = "submission.json"

def run_queries_and_generate_submission():
    """Reads benchmark queries, calls the API, and generates submission.json."""
    
    # 1. Load the benchmark queries
    try:
        with open(BENCHMARK_FILE, 'r', encoding='utf-8') as f:
            benchmark_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Benchmark file not found at {BENCHMARK_FILE}. Please check the path.")
        return

    # Initialize results. We use a dictionary to group results by 'id', 
    # handling cases where one ID (like '3') might be used multiple times.
    grouped_results = {}
    
    # 2. Iterate through the list of test objects inside the 'tests' key
    # CRITICAL FIX: Loop over benchmark_data['tests'] instead of benchmark_data['queries']
    if 'tests' not in benchmark_data:
        print("Error: JSON structure invalid. 'tests' key not found at the root.")
        return
        
    for query_data in benchmark_data['tests']:
        query_id = str(query_data['id']) # Store ID as string to match desired JSON output format
        query_type = query_data['type'].lower() # e.g., 'prefix', 'fuzzy'
        query_string = query_data['query']
        
        # Construct the full API URL, e.g., http://127.0.0.1:8000/search/prefix?q=boc
        endpoint = f"{API_BASE_URL}/{query_type}"
        params = {"q": query_string}
        
        print(f"Running Query {query_id} ({query_type}): {query_string}...")
        
        try:
            # Make the API call to your running Uvicorn server
            response = requests.get(endpoint, params=params)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            
            # The API returns a list of names. For the final submission, you need
            # to aggregate results from queries with the same ID.
            
            # NOTE: Your example shows duplicate IDs (3). The standard submission format
            # expects one result per ID key. Since the assignment example is ambiguous 
            # about how to combine results for duplicate IDs, we will simply use the
            # result of the *last* query executed for that ID, as is standard in simple 
            # dictionary assignment. For the final submission, ensure you use the 
            # fixed query set provided in the assignment's official `benchmark_queries.json`.
            
            grouped_results[query_id] = response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"  --> Failed to call API for Query {query_id}: {e}")
            grouped_results[query_id] = [f"API Error: {e}"]
        
    # 3. Write the final submission.json file
    submission_data = {"results": grouped_results}
    
    with open(SUBMISSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(submission_data, f, indent=2)
        
    print("\n--- Process Complete ---")
    print(f"Successfully generated {SUBMISSION_FILE} in the current directory.")
    
if __name__ == "__main__":
    # Wait a moment to ensure the server is fully ready
    time.sleep(1) 
    run_queries_and_generate_submission()
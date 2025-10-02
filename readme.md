High-Performance Medicine Search System (PostgreSQL + FastAPI)
This project implements a highly optimized search system for a large medicine dataset (approx. 280,000 unique records) using PostgreSQL's advanced indexing features and exposing the functionality via a Python FastAPI backend.

The solution is designed to handle four critical search types with near-instantaneous latency: Prefix, Substring, Fuzzy (typo-tolerant), and Full-Text Search.

Prerequisites
PostgreSQL Server: Must be installed and running (default port 5432).

Database Credentials: The user postgres must have the password set to skanda, and a database named database1 must exist.

Python 3.10+: Installed on your system (the project was built and tested using Python 3.13).

Setup and Installation
Clone/Download Repository: Place all files in your local project folder.

Install Python Dependencies: Use the Python interpreter you intend to run the API with (e.g., Python 3.13) to install required packages:

python.exe -m pip install psycopg2-binary fastapi uvicorn requests

Run Instructions
Follow these steps sequentially to set up the database and start the API server:

1. Setup Database Schema (Indexes and Table)
Execute the schema.sql file in your PostgreSQL management tool (like pgAdmin) against the database1. This step is crucial as it creates the medicines table and all the necessary GIN and B-tree indexes for high performance.

2. Import Data
Run the import_data.py script to read the 26 JSON files (A.json to Z.json) from the /data folder and perform bulk insertion into the medicines table.

python.exe import_data.py
# Expected output: Data import successful!

(Note: The script uses ON CONFLICT DO NOTHING and handles duplicate IDs found in the source data.)

3. Start the API Server
Run the search_api.py file to start the FastAPI server. Keep this terminal window open.

python.exe -m uvicorn search_api:app --reload
# Expected output: Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000)

4. Run Benchmark and Generate Submission
Open a second terminal window and run the run_benchmark.py script. This client script calls the running API endpoints using the queries specified in benchmark_queries.json and generates the final submission.json file.

python.exe run_benchmark.py
# Expected output: Successfully generated submission.json in the current directory.

Detailed Description of Performance Approach
Performance relies entirely on PostgreSQL's indexing capabilities, minimizing costly full table scans.

Search Type

PostgreSQL Tool

Index Strategy

Performance

Prefix Search

lower(name) LIKE 'query%'

B-tree Index (idx_medicines_name_lower)

Achieves sub-millisecond response times by seeking directly to the starting characters.

Full-Text Search

ts_rank / tsvector

GIN Index (idx_medicines_search_tsv)

Achieves sub-millisecond response times by indexing words across multiple fields (Name, Composition) and efficiently calculating relevance.

Substring/Fuzzy Search

similarity() / %%

GIN Trigram Index (idx_medicines_name_trgm)

Required for high performance. This index allows the database to instantly measure the similarity between strings, turning slow wildcard lookups (%query%) into fast, index-based sorting operations. The API uses this strategy to achieve high throughput for both typo-tolerant and general substring searches.

The system is highly optimized, with Full-Text and Prefix searches demonstrating less than 0.1 ms latency based on the generated benchmark data.
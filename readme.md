# High-Performance Medicine Search System (PostgreSQL + FastAPI)

This project implements a highly optimized search system for a large medicine dataset (~280,000 unique records) using **PostgreSQL** with advanced indexing features and exposing the functionality via a **Python FastAPI** backend.  

The system handles four critical search types with near-instantaneous latency:
- **Prefix Search**
- **Substring Search**
- **Fuzzy (typo-tolerant) Search**
- **Full-Text Search**

---

## Prerequisites
- **PostgreSQL Server:** Must be installed and running (default port 5432).  
- **Python 3.10+** installed on your system (tested with Python 3.13).  

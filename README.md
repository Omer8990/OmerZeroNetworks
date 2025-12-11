# SpaceX Launch Data Ingestion & Analytics Platform

[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

A robust, production-ready data engineering project that ingests SpaceX launch data, stores it in PostgreSQL, and enables large-scale analytics with Trino.

This pipeline is designed with an **ELT (Extract, Load, Transform)** philosophy, featuring an intelligent incremental loading strategy, data validation, and automated aggregation.

## Architecture Overview

The platform is composed of a few key services orchestrated by Docker Compose. The ingestion script fetches data from the SpaceX API, loads it into a raw data table in PostgreSQL, and then triggers a transformation within the database to generate analytical aggregates. Trino provides a federated query layer on top of PostgreSQL for high-performance analytics.

```
+------------------+      +-------------------------+      +---------------------+
|                  |      |                         |      |                     |
|  SpaceX v4 API   +------>  Python Ingestion Service <------>   PostgreSQL DB       |
|                  |      |    (ELT Script)         |      | (Raw & Agg Tables)  |
+------------------+      +-------------------------+      +----------^----------+
                                     |                             |
                                     | (SQL Queries)               |
                                     v                             |
+------------------------------------------------------------------+
|   Trino (Federated Query Engine)                                 |
|                                                                  |
|   +-----------------------+      +------------------------+      |
|   |  Business Intelligence|      |                        |      |
|   |    (e.g., DataGrip)   |------>                        <------|  Data Analysts      |
|   +-----------------------+      |    Trino Coordinator   |      |  (Ad-hoc SQL)       |
|                                  |                        |      |                     |
|                                  +------------------------+      +---------------------+
+------------------------------------------------------------------+
```

---

## Key Features

*   **Automated ELT Pipeline**: Implements a full Extract, Load, Transform workflow.
*   **Intelligent Ingestion Strategy**:
    *   **Automatic Backfill**: On the first run, it performs a full historical backfill of all past SpaceX launches.
    *   **Incremental Loading**: On subsequent runs, it only fetches launches newer than the latest data in the database, ensuring efficiency.
*   **Resilient & Robust**:
    *   **API Bug Workaround**: Includes client-side filtering to handle known inconsistencies in the SpaceX API (e.g., filtering `upcoming` launches).
    *   **Graceful Validation**: Uses Pydantic for data validation but is designed to log and skip individual malformed records rather than failing the entire pipeline, prioritizing robustness.
*   **Idempotent & Safe**: Database operations are idempotent. Inserts use `ON CONFLICT DO NOTHING`, and table creation scripts use `IF NOT EXISTS`, making pipeline runs safe to repeat.
*   **Data Transformation in the Warehouse**: Post-load transformation is handled by SQL within PostgreSQL, following modern ELT best practices. This includes:
    *   **Data Enrichment**: Calculating `launch_delay_seconds` on the fly.
    *   **Automated Aggregation**: Updating a summary table (`launch_aggregates`) after each run.
*   **Analytics-Ready**: Integrated with **Trino**, allowing users to run fast, federated queries on the PostgreSQL data, suitable for BI tools and ad-hoc analysis.
*   **Professional Codebase**:
    *   Fully type-hinted and formatted with Black.
    *   Comprehensive logging across all services.
    *   Clean, modular project structure.

---

## Technology Stack

*   **Orchestration**: Docker, Docker Compose
*   **Programming Language**: Python 3.11
*   **Data Ingestion**: `requests` for API communication, `Pydantic` for data validation.
*   **Database**: PostgreSQL 16
*   **Data Warehouse / Query Engine**: Trino
*   **Python Libraries**: See `requirements.txt`

---

## Setup and Configuration

### Prerequisites
*   Docker & Docker Compose
*   Python 3.11+
*   An internet connection

### 1. Clone the Repository
```bash
git clone https://github.com/Omer8990/OmerZeroNetworks
cd OmerHaimovichZeroNetworksHomeAssignment
```

### 2. Configure Environment Variables
Create a `.env` file in the project root. The application reads database credentials and API settings from this file.

```dotenv
# .env
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
POSTGRES_DB=test_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
API_URL=https://api.spacexdata.com/v4/launches/query
```

### 3. Install Dependencies
It's highly recommended to use a Python virtual environment.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Launch Services
This command starts the PostgreSQL and Trino containers in detached mode.
```bash
docker-compose up -d
```
You can check the health of the services with `docker-compose ps`. Wait for both to report `(healthy)`.

---

## Running the Pipeline

To run the full ELT process, execute the main application module from the project root.

```bash
PYTHONPATH=./src python3 -m launch_ingester.main
```
*   **First Run (Backfill)**: This will fetch all historical launch data from the SpaceX API. It may take a few minutes. You will see detailed logs of the process.
*   **Subsequent Runs (Incremental)**: This will only fetch new launch data. If no new data is found, the process will complete quickly.

The `PYTHONPATH=./src` prefix is required to ensure the Python interpreter can correctly locate the `launch_ingester` package.

---

## Querying and Analytics

Data can be queried directly from PostgreSQL, but the recommended approach is to use the powerful Trino query engine, which is accessible on port `8080`.

### Connecting a SQL Client (Recommended)
Connect your favorite SQL client (e.g., DataGrip, DBeaver) to Trino with these settings:
-   **Host**: `localhost`
-   **Port**: `8080`
-   **User**: `admin` 
-   **URL**: `jdbc:trino://localhost:8080`


You can then explore and query the following tables:
-   `raw_launches`: Contains the raw, unmodified JSON data for every launch.
-   `launch_aggregates`: A summary table with key metrics, updated after every ingestion run.

### Using the Trino CLI
For quick ad-hoc queries, you can use the Trino CLI inside the Docker container.

1.  **Access the CLI:**
    ```bash
    docker exec -it trino trino
    ```

2.  **Run Queries:**
    Remember to fully qualify your table names (`<catalog>.<schema>.<table>`).
    ```sql
    -- Check raw data count
    SELECT count(*) FROM postgresql.public.raw_launches;

    -- View aggregated metrics
    SELECT * FROM postgresql.public.launch_aggregates;

    ```

### Running Pre-defined SQL Analysis
The `sql/` directory contains sample analytical queries. You can execute them directly:

```bash
# Get year-over-year launch performance
docker exec -i trino trino --execute "$(cat sql/01_launch_performance_over_time.sql)"

# Find the top 5 launches by payload mass
docker exec -i trino trino --execute "$(cat sql/02_top_payload_mass.sql)"

# Analyze launch delay patterns
docker exec -i trino trino --execute "$(cat sql/03_average_launch_delay.sql)"

# Find the launch site utilization stats
docker exec -i trino trino --execute "$(cat sql/04_launch_site_utilization.sql)"
```

---

## Design Deep Dive

### ELT (Extract, Load, Transform)
This project follows an ELT paradigm. Raw data is first loaded into the `raw_launches` table with minimal processing. Transformations then run *inside the database*, which is highly scalable. The main transformation is the `update_launch_aggregates` function, which reads from the raw table and populates the aggregate table.

### Data Storage: JSONB
Raw launch data is stored in a `JSONB` column in PostgreSQL. This approach provides:
-   **Schema Flexibility**: No data is lost, even if the API adds new fields. The pipeline will not break.
-   **Performance**: `JSONB` is indexed and allows for efficient querying of nested fields.

### Idempotency
Every part of the pipeline is designed to be safely re-runnable.
-   **Ingestion**: `ON CONFLICT (id) DO NOTHING` prevents duplicate launch records.
-   **Aggregation**: `ON CONFLICT (id) DO UPDATE` ensures the aggregate table is always up-to-date.
-   **Table Creation**: `CREATE TABLE IF NOT EXISTS` prevents errors on subsequent runs.

---

## Project Structure
```
.
├── docker/                  # Docker configurations
│   └── trino-catalog/       # Trino catalog properties
├── sql/                     # SQL scripts for analysis and table creation
├── src/
│   └── launch_ingester/     # Main Python package
│       ├── api/             # SpaceX API client
│       ├── database/        # PostgreSQL database operations
│       ├── models/          # Pydantic data models
│       ├── processors/      # Core ingestion logic (backfill/incremental)
│       ├── config.py        # Configuration loading
│       └── main.py          # Application entry point
├── .env                     # Environment variable definitions (user-created)
├── docker-compose.yml       # Service orchestration
├── main.py                  # Project root entry point
└── requirements.txt         # Python dependencies
```

---

## Stopping Services
To stop all running Docker containers, use:
```bash
docker-compose down
```
To remove the persistent PostgreSQL data, add the `-v` flag: `docker-compose down -v`.

# Zero Networks Home Assignment

This project ingests launch data from the SpaceX API and stores it in a PostgreSQL database. It's designed with a professional Python package structure and implements a robust backfill and incremental loading strategy.

## Code Quality and Best Practices

This project has been refactored to adhere to modern Python development standards:

- **Structured Package**: The code is organized into a clear package structure within `src/launch_ingester`.
- **Logging**: All operations are logged using Python's `logging` module, providing clear visibility into the ingestion process. `print()` statements have been removed.
- **Type Hinting**: The code is fully type-hinted for improved readability and maintainability.
- **Connection Management**: Database connections are handled safely and efficiently using context managers.
- **Clear Entry Point**: The application logic is separated from the execution entry point (`main.py`).

## Project Structure

The `src` directory is organized as a Python package with the following structure:

```
src/
└───launch_ingester/
    ├───__init__.py         # Initializes package-wide logging.
    ├───main.py             # The application's main entry point.
    ├───config.py           # Handles loading and validating environment variables.
    ├───api/
    │   ├───__init__.py
    │   └───client.py       # SpaceX API client for fetching launch data.
    ├───database/
    │   ├───__init__.py
    │   └───operations.py   # Database connection management and CRUD operations.
    ├───models/
    │   ├───__init__.py
    │   └───launch.py       # Pydantic models for SpaceX launch and payload data.
    └───processors/
        ├───__init__.py
        └───ingestion.py    # Core logic for orchestrating data ingestion.
```

## Design Choices

**Assumption regarding 'Latest Data'**: The requirements requested fetching "latest data" while also requiring "Year-over-Year" SQL analysis. Fetching only the single latest launch would make the SQL analysis impossible.
**Decision**: The pipeline is designed to perform an initial historical backfill of all past launches to enable analytics. Subsequent runs operate in an incremental mode, fetching only launches that have occurred since the most recent launch stored in the database. This satisfies both requirements.

## Prerequisites

- Docker & Docker Compose
- Python 3.11

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd OmerHaimovichZeroNetworksHomeAssignment
   ```

2. **Environment Variables:**
   The project uses a `.env` file to manage environment variables. Make sure it has the following content. Note the `API_URL` is pointed to the `v4/launches/query` endpoint.
   ```
   POSTGRES_USER=test_user
   POSTGRES_PASSWORD=test_password
   POSTGRES_DB=test_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   API_URL=https://api.spacexdata.com/v4/launches/query
   ```

3. **Install Python dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Start the services:**
   This will start the PostgreSQL and Trino containers in the background.
   ```bash
   docker-compose up -d
   ```
   Wait for the services to be healthy. You can check the status with `docker-compose ps`.

## Run the Ingestion

To fetch SpaceX launch data, run the following command from the root of the project:

```bash
PYTHONPATH=./src python3 -m launch_ingester.main
```

**Note on `PYTHONPATH`**: We prepend `PYTHONPATH=./src` to the command to temporarily add the `src` directory to Python's path. This allows the interpreter to correctly find and import the `launch_ingester` package, which is necessary for the refactored project structure.

- **First Run**: This will perform a "backfill", fetching all past launches. This may take a few moments.
- **Subsequent Runs**: This will perform an "incremental load", fetching only launches that are newer than the latest one in your database.

## Verify the Data

You can query the data from PostgreSQL using the Trino CLI.

1. **Access the Trino CLI:**
   ```bash
   docker exec -it trino trino
   ```

2. **Query the data:**
   Once in the Trino CLI, you can check the number of launches ingested.
   ```sql
   SELECT count(*) FROM postgresql.public.raw_launches;
   ```

   To see the details of a specific launch:
   ```sql
   SELECT * FROM postgresql.public.raw_launches LIMIT 10;
   ```

   To exit the Trino CLI, type `quit`.

## Stop the services

To stop the Docker containers, run:
```bash
docker-compose down
```

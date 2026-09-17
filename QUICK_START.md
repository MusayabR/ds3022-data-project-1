# Quick Start Guide

## Installation

```bash
cd /Users/musa/ds3022-project
pip install -r requirements.txt
```

## Running the Pipeline

Execute the 4-stage pipeline in order:

### 1. Load Data
```bash
python load.py
```
- Downloads all 2024 NYC taxi data (yellow & green) from the TLC website
- Creates DuckDB database with 3 tables
- Shows raw row counts
- First run takes ~5-10 minutes to download data (~100MB)
- Logs: `load.log`

### 2. Clean Data  
```bash
python clean.py
```
- Removes invalid records (duplicates, 0 passengers, 0 miles, >100 miles, >86400 sec)
- Verifies all cleaning conditions
- Creates cleaned tables
- Logs: `clean.log`

### 3. Transform Data
```bash
python transform.py
```
- Adds 6 calculated columns:
  - `trip_co2_kgs` (CO2 emissions)
  - `avg_mph` (average speed)
  - `hour_of_day` (0-23)
  - `day_of_week` (Mon-Sun)
  - `week_of_year` (1-52)
  - `month_of_year` (1-12)
- Creates transformed tables
- Logs: `transform.log`

### 4. Analyze Data
```bash
python analysis.py
```
- Generates analysis reports for both taxi types:
  1. Largest CO2 trip
  2. Most/least carbon-heavy hours
  3. Most/least carbon-heavy days of week
  4. Most/least carbon-heavy weeks
  5. Most/least carbon-heavy months
- Creates `co2_by_month.png` visualization
- Logs: `analysis.log`

## Key Files Generated

| File | Purpose |
|------|---------|
| `emissions.duckdb` | Main database (excluded from git) |
| `*.parquet` | Downloaded taxi data (excluded from git) |
| `*.log` | Stage-specific logs (excluded from git) |
| `co2_by_month.png` | Analysis visualization |

## Optional: DBT Models

For extra 6 points, use DBT to perform transformations:

```bash
# Install DBT (optional)
pip install dbt-duckdb

# Run DBT models
cd dbt
dbt run
cd ..
```

Models location: `dbt/models/staging/`
- `stg_yellow_taxi_transformed.sql`
- `stg_green_taxi_transformed.sql`

## Database Inspection

To examine the database directly:

```python
import duckdb
con = duckdb.connect('emissions.duckdb')

# List all tables
print(con.execute("SELECT table_name FROM information_schema.tables").fetchall())

# Query a table
print(con.execute("SELECT * FROM yellow_taxi_transformed LIMIT 5").fetchall())

con.close()
```

## Performance Notes

- Load stage: ~5-10 min (first run with downloads), <1 min (subsequent runs)
- Clean stage: ~30 seconds
- Transform stage: ~2 minutes  
- Analysis stage: ~3 minutes
- **Total time: ~15 minutes first run, ~6 minutes subsequent runs**

## Troubleshooting

**Q: Network timeout during load**
- A: Files are cached locally. Delete the parquet file and retry.

**Q: DuckDB error - "table does not exist"**
- A: Run stages in order. Each stage depends on the previous one.

**Q: Plot not saving**
- A: Ensure matplotlib is installed. Check `analysis.log` for errors.

**Q: Can't find emissions.duckdb**
- A: Run load.py first to create the database.

## Code Structure

```
load.py         → Creates database and loads raw data
  ↓
clean.py        → Removes invalid records
  ↓
transform.py    → Adds calculated columns
  ↓
analysis.py     → Generates reports and plots
```

Each stage creates its own log file for monitoring and debugging.

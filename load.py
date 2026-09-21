import duckdb
import logging
import os
import time
import urllib.request
import ssl
import certifi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('load.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def load_emissions(con):
    """Load the vehicle_emissions lookup table from the csv."""
    con.execute("""
        DROP TABLE IF EXISTS vehicle_emissions;
        CREATE TABLE vehicle_emissions AS
        SELECT * FROM read_csv_auto('data/vehicle_emissions.csv');
    """)
    n = con.execute("SELECT COUNT(*) FROM vehicle_emissions").fetchone()[0]
    logger.info(f"vehicle_emissions: {n} rows loaded")


def download_file(url, path):
    """Download one parquet file, retrying a few times."""
    if os.path.exists(path):
        return  # already downloaded
    tmp = path + ".tmp"
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            ctx = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(req, context=ctx) as r, open(tmp, "wb") as f:
                f.write(r.read())
            os.rename(tmp, path)
            logger.info(f"downloaded {os.path.basename(path)}")
            return
        except Exception as e:
            logger.warning(f"download attempt {attempt} failed for {url} - {e}")
            time.sleep(5)
    raise Exception(f"could not download {url}")


def load_trips(con, color):
    """Load all 12 months of 2024 trips for one taxi color."""
    table = f"{color}_trips"
    # yellow uses tpep_, green uses lpep_
    prefix = "tpep" if color == "yellow" else "lpep"

    con.execute(f"DROP TABLE IF EXISTS {table}")
    con.execute(f"""
        CREATE TABLE {table} (
            VendorID INTEGER,
            pickup_time TIMESTAMP,
            dropoff_time TIMESTAMP,
            passenger_count BIGINT,
            trip_distance DOUBLE
        )
    """)

    for month in range(1, 13):
        url = f"{BASE_URL}/{color}_tripdata_2024-{month:02d}.parquet"
        path = f"data/{color}_tripdata_2024-{month:02d}.parquet"
        try:
            download_file(url, path)
            con.execute(f"""
                INSERT INTO {table}
                SELECT VendorID,
                       {prefix}_pickup_datetime,
                       {prefix}_dropoff_datetime,
                       passenger_count,
                       trip_distance
                FROM read_parquet('{path}')
            """)
            logger.info(f"{table}: loaded month {month:02d}/2024")
        except Exception as e:
            logger.error(f"{table}: failed on month {month:02d} - {e}")

    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    logger.info(f"{table}: {n:,} rows loaded (raw)")


def print_stats(con, table):
    """Log some basic stats for a trip table."""
    row = con.execute(f"""
        SELECT COUNT(*),
               ROUND(AVG(trip_distance), 2),
               MAX(trip_distance),
               ROUND(AVG(passenger_count), 2),
               MIN(pickup_time),
               MAX(pickup_time)
        FROM {table}
    """).fetchone()
    logger.info(f"{table} stats -> rows: {row[0]:,}, avg miles: {row[1]}, "
                f"max miles: {row[2]}, avg passengers: {row[3]}, "
                f"first pickup: {row[4]}, last pickup: {row[5]}")


def main():
    """Connect to duckdb and load all three tables."""
    con = None
    try:
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        load_emissions(con)
        for color in ["yellow", "green"]:
            load_trips(con, color)
            print_stats(con, f"{color}_trips")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    main()
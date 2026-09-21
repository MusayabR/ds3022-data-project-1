import duckdb
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('clean.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# (rule name, WHERE clause that finds a bad trip)
RULES = [
    ("0 passengers", "passenger_count = 0"),
    ("0 miles", "trip_distance = 0"),
    ("over 100 miles", "trip_distance > 100"),
    ("over 1 day", "DATE_DIFF('second', pickup_time, dropoff_time) > 86400"),
    ("dropoff not after pickup", "dropoff_time <= pickup_time"),
    ("pickup not in 2024", "YEAR(pickup_time) != 2024"),
]


def remove_duplicates(con, table):
    """Keep only the first copy of each trip using ROW_NUMBER()."""
    before = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    con.execute(f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT * EXCLUDE (copy_number) FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY VendorID, pickup_time, dropoff_time,
                             passenger_count, trip_distance
            ) AS copy_number
            FROM {table}
        ) WHERE copy_number = 1;
    """)
    after = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    logger.info(f"{table}: removed {before - after} duplicates")


def remove_bad_trips(con, table):
    """DELETE every trip that breaks one of the rules."""
    for name, where in RULES:
        n = con.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}").fetchone()[0]
        con.execute(f"DELETE FROM {table} WHERE {where}")
        logger.info(f"{table}: removed {n} trips ({name})")


def verify(con, table):
    """Re-run each check, every count should now be 0."""
    dupes = con.execute(f"""
        SELECT COUNT(*) FROM (
            SELECT ROW_NUMBER() OVER (
                PARTITION BY VendorID, pickup_time, dropoff_time,
                             passenger_count, trip_distance
            ) AS copy_number
            FROM {table}
        ) WHERE copy_number > 1
    """).fetchone()[0]
    logger.info(f"CHECK {table} duplicates: {dupes}")

    for name, where in RULES:
        n = con.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}").fetchone()[0]
        logger.info(f"CHECK {table} {name}: {n}")

    total = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    logger.info(f"{table}: {total} rows after cleaning")


def clean_tables():
    """Clean both trip tables and verify the results."""
    con = None

    try:
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        for table in ["yellow_trips", "green_trips"]:
            remove_duplicates(con, table)
            remove_bad_trips(con, table)
            verify(con, table)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    clean_tables()
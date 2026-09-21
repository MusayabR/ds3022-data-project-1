import duckdb
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('transform.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def add_columns(con, table):
    """Add the six new columns (safe to re-run)."""
    con.execute(f"""
        ALTER TABLE {table} ADD COLUMN IF NOT EXISTS trip_co2_kgs DOUBLE;
        ALTER TABLE {table} ADD COLUMN IF NOT EXISTS avg_mph DOUBLE;
        ALTER TABLE {table} ADD COLUMN IF NOT EXISTS hour_of_day INTEGER;
        ALTER TABLE {table} ADD COLUMN IF NOT EXISTS day_of_week INTEGER;
        ALTER TABLE {table} ADD COLUMN IF NOT EXISTS week_of_year INTEGER;
        ALTER TABLE {table} ADD COLUMN IF NOT EXISTS month_of_year INTEGER;
    """)
    logger.info(f"{table}: columns added")


def fill_columns(con, color):
    """Fill in co2, mph and the date parts for one taxi color."""
    table = f"{color}_trips"
    # co2 factor is looked up from vehicle_emissions, not hard-coded
    con.execute(f"""
        UPDATE {table} SET
            trip_co2_kgs = trip_distance * (
                SELECT co2_grams_per_mile FROM vehicle_emissions
                WHERE vehicle_type = '{color}_taxi'
            ) / 1000,
            avg_mph = trip_distance / (DATE_DIFF('second', pickup_time, dropoff_time) / 3600.0),
            hour_of_day = HOUR(pickup_time),
            day_of_week = DAYOFWEEK(pickup_time),
            week_of_year = WEEKOFYEAR(pickup_time),
            month_of_year = MONTH(pickup_time);
    """)
    logger.info(f"{table}: trip_co2_kgs, avg_mph, hour_of_day, day_of_week, "
                f"week_of_year, month_of_year filled in")


def print_stats(con, table):
    """Log a quick summary of the new columns."""
    stats = con.execute(f"""
        SELECT COUNT(*),
               ROUND(SUM(trip_co2_kgs), 2),
               ROUND(AVG(trip_co2_kgs), 3),
               ROUND(AVG(avg_mph), 2)
        FROM {table}
    """).fetchone()
    logger.info(f"{table}: rows={stats[0]}, total_co2_kgs={stats[1]}, "
                f"avg_co2_kgs={stats[2]}, avg_mph={stats[3]}")


def transform_tables():
    """Run the transformations on both trip tables."""
    con = None

    try:
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        for color in ["yellow", "green"]:
            add_columns(con, f"{color}_trips")
            fill_columns(con, color)
            print_stats(con, f"{color}_trips")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    transform_tables()
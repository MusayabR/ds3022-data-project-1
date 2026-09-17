import duckdb
import logging

# NOTE: For additional 6 points, DBT models are also provided in dbt/models/staging/:
# - stg_yellow_taxi_transformed.sql
# - stg_green_taxi_transformed.sql
# Run "dbt run" in the dbt/ directory to execute these models.

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='transform.log',
    filemode='w'
)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='transform.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

def transform_trips() -> None:
    """
    Transform cleaned taxi trip data by adding calculated columns:
    1. trip_co2_kgs: CO2 output calculated from trip distance and vehicle emissions lookup
    2. avg_mph: Average miles per hour (distance / duration)
    3. hour_of_day: Hour extracted from pickup_time
    4. day_of_week: Day of week from pickup_time
    5. week_of_year: Week number from pickup_time
    6. month_of_year: Month from pickup_time
    """
    con = None
    
    try:
        # Connect to DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")
        
        # Transform Yellow Taxi Data
        logger.info("=== TRANSFORMING YELLOW TAXI DATA ===")
        logger.info("Creating yellow_taxi_transformed table...")
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS yellow_taxi_transformed AS
            SELECT 
                ytc.*,
                ROUND((ytc.trip_distance * ve.co2_grams_per_mile / 1000)::NUMERIC, 2) as trip_co2_kgs,
                ROUND((ytc.trip_distance / (ytc.duration_seconds / 3600.0))::NUMERIC, 2) as avg_mph,
                EXTRACT(HOUR FROM ytc.pickup_time) as hour_of_day,
                DAYNAME(ytc.pickup_time) as day_of_week,
                EXTRACT(WEEK FROM ytc.pickup_time) as week_of_year,
                EXTRACT(MONTH FROM ytc.pickup_time) as month_of_year
            FROM yellow_taxi_cleaned ytc
            JOIN vehicle_emissions ve ON ve.vehicle_type = 'yellow_taxi'
        """)
        logger.info("Created yellow_taxi_transformed table")
        
        # Verify columns
        yellow_cols = con.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'yellow_taxi_transformed' ORDER BY column_name"
        ).fetchall()
        print(f"Yellow Taxi - Columns: {[col[0] for col in yellow_cols]}")
        logger.info(f"Yellow taxi columns: {[col[0] for col in yellow_cols]}")
        
        # Verify calculated columns are not null
        yellow_co2_nulls = con.execute(
            "SELECT COUNT(*) FROM yellow_taxi_transformed WHERE trip_co2_kgs IS NULL"
        ).fetchall()[0][0]
        print(f"Yellow Taxi - NULL trip_co2_kgs values: {yellow_co2_nulls}")
        logger.info(f"Yellow taxi NULL CO2 values: {yellow_co2_nulls}")
        
        yellow_mph_nulls = con.execute(
            "SELECT COUNT(*) FROM yellow_taxi_transformed WHERE avg_mph IS NULL"
        ).fetchall()[0][0]
        print(f"Yellow Taxi - NULL avg_mph values: {yellow_mph_nulls}")
        logger.info(f"Yellow taxi NULL MPH values: {yellow_mph_nulls}")
        
        yellow_count = con.execute("SELECT COUNT(*) FROM yellow_taxi_transformed").fetchall()[0][0]
        print(f"Yellow Taxi - Total transformed rows: {yellow_count:,}\n")
        logger.info(f"Yellow taxi transformed rows: {yellow_count}")
        
        # Transform Green Taxi Data
        logger.info("=== TRANSFORMING GREEN TAXI DATA ===")
        logger.info("Creating green_taxi_transformed table...")
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS green_taxi_transformed AS
            SELECT 
                gtc.*,
                ROUND((gtc.trip_distance * ve.co2_grams_per_mile / 1000)::NUMERIC, 2) as trip_co2_kgs,
                ROUND((gtc.trip_distance / (gtc.duration_seconds / 3600.0))::NUMERIC, 2) as avg_mph,
                EXTRACT(HOUR FROM gtc.pickup_time) as hour_of_day,
                DAYNAME(gtc.pickup_time) as day_of_week,
                EXTRACT(WEEK FROM gtc.pickup_time) as week_of_year,
                EXTRACT(MONTH FROM gtc.pickup_time) as month_of_year
            FROM green_taxi_cleaned gtc
            JOIN vehicle_emissions ve ON ve.vehicle_type = 'green_taxi'
        """)
        logger.info("Created green_taxi_transformed table")
        
        # Verify columns
        green_cols = con.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'green_taxi_transformed' ORDER BY column_name"
        ).fetchall()
        print(f"Green Taxi - Columns: {[col[0] for col in green_cols]}")
        logger.info(f"Green taxi columns: {[col[0] for col in green_cols]}")
        
        # Verify calculated columns are not null
        green_co2_nulls = con.execute(
            "SELECT COUNT(*) FROM green_taxi_transformed WHERE trip_co2_kgs IS NULL"
        ).fetchall()[0][0]
        print(f"Green Taxi - NULL trip_co2_kgs values: {green_co2_nulls}")
        logger.info(f"Green taxi NULL CO2 values: {green_co2_nulls}")
        
        green_mph_nulls = con.execute(
            "SELECT COUNT(*) FROM green_taxi_transformed WHERE avg_mph IS NULL"
        ).fetchall()[0][0]
        print(f"Green Taxi - NULL avg_mph values: {green_mph_nulls}")
        logger.info(f"Green taxi NULL MPH values: {green_mph_nulls}")
        
        green_count = con.execute("SELECT COUNT(*) FROM green_taxi_transformed").fetchall()[0][0]
        print(f"Green Taxi - Total transformed rows: {green_count:,}\n")
        logger.info(f"Green taxi transformed rows: {green_count}")
        
        con.close()
        logger.info("Data transformation completed successfully")
        print("Transformation complete!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
        if con:
            con.close()

if __name__ == "__main__":
    transform_trips()
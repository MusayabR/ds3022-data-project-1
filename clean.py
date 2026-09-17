import duckdb
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='clean.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

def clean_trips() -> None:
    """
    Clean taxi trip data by removing:
    1. Duplicate trips
    2. Trips with 0 passengers
    3. Trips with 0 miles in length
    4. Trips longer than 100 miles
    5. Trips lasting more than 1 day (86400 seconds)
    """
    con = None
    
    try:
        # Connect to DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")
        
        # Process Yellow Taxi Data
        logger.info("=== CLEANING YELLOW TAXI DATA ===")
        
        # Create cleaned yellow taxi table
        logger.info("Creating cleaned yellow_taxi table...")
        con.execute("""
            CREATE TABLE IF NOT EXISTS yellow_taxi_cleaned AS
            SELECT DISTINCT *
            FROM yellow_taxi
            WHERE passenger_count > 0
            AND trip_distance > 0
            AND trip_distance <= 100
            AND duration_seconds <= 86400
        """)
        logger.info("Created yellow_taxi_cleaned table")
        
        # Verify cleaning conditions for yellow taxis
        logger.info("Verifying yellow taxi cleaning conditions...")
        
        # Check for duplicates
        dup_check = con.execute("""
            SELECT COUNT(*) FROM (
                SELECT * FROM yellow_taxi_cleaned
                EXCEPT
                SELECT DISTINCT * FROM yellow_taxi_cleaned
            )
        """).fetchall()[0][0]
        print(f"Yellow Taxi - Duplicates found after cleaning: {dup_check}")
        logger.info(f"Yellow taxi duplicates after cleaning: {dup_check}")
        
        # Check for 0 passengers
        zero_pass = con.execute(
            "SELECT COUNT(*) FROM yellow_taxi_cleaned WHERE passenger_count = 0"
        ).fetchall()[0][0]
        print(f"Yellow Taxi - Zero passengers trips: {zero_pass}")
        logger.info(f"Yellow taxi zero passengers: {zero_pass}")
        
        # Check for 0 miles
        zero_miles = con.execute(
            "SELECT COUNT(*) FROM yellow_taxi_cleaned WHERE trip_distance = 0"
        ).fetchall()[0][0]
        print(f"Yellow Taxi - Zero miles trips: {zero_miles}")
        logger.info(f"Yellow taxi zero miles: {zero_miles}")
        
        # Check for > 100 miles
        over_100 = con.execute(
            "SELECT COUNT(*) FROM yellow_taxi_cleaned WHERE trip_distance > 100"
        ).fetchall()[0][0]
        print(f"Yellow Taxi - Trips over 100 miles: {over_100}")
        logger.info(f"Yellow taxi over 100 miles: {over_100}")
        
        # Check for > 86400 seconds
        over_day = con.execute(
            "SELECT COUNT(*) FROM yellow_taxi_cleaned WHERE duration_seconds > 86400"
        ).fetchall()[0][0]
        print(f"Yellow Taxi - Trips over 1 day duration: {over_day}")
        logger.info(f"Yellow taxi over 1 day: {over_day}")
        
        yellow_before = con.execute("SELECT COUNT(*) FROM yellow_taxi").fetchall()[0][0]
        yellow_after = con.execute("SELECT COUNT(*) FROM yellow_taxi_cleaned").fetchall()[0][0]
        yellow_removed = yellow_before - yellow_after
        print(f"Yellow Taxi - Rows before: {yellow_before:,}, After: {yellow_after:,}, Removed: {yellow_removed:,}\n")
        logger.info(f"Yellow taxi: {yellow_before} -> {yellow_after} ({yellow_removed} removed)")
        
        # Process Green Taxi Data
        logger.info("=== CLEANING GREEN TAXI DATA ===")
        
        # Create cleaned green taxi table
        logger.info("Creating cleaned green_taxi table...")
        con.execute("""
            CREATE TABLE IF NOT EXISTS green_taxi_cleaned AS
            SELECT DISTINCT *
            FROM green_taxi
            WHERE passenger_count > 0
            AND trip_distance > 0
            AND trip_distance <= 100
            AND duration_seconds <= 86400
        """)
        logger.info("Created green_taxi_cleaned table")
        
        # Verify cleaning conditions for green taxis
        logger.info("Verifying green taxi cleaning conditions...")
        
        # Check for duplicates
        dup_check = con.execute("""
            SELECT COUNT(*) FROM (
                SELECT * FROM green_taxi_cleaned
                EXCEPT
                SELECT DISTINCT * FROM green_taxi_cleaned
            )
        """).fetchall()[0][0]
        print(f"Green Taxi - Duplicates found after cleaning: {dup_check}")
        logger.info(f"Green taxi duplicates after cleaning: {dup_check}")
        
        # Check for 0 passengers
        zero_pass = con.execute(
            "SELECT COUNT(*) FROM green_taxi_cleaned WHERE passenger_count = 0"
        ).fetchall()[0][0]
        print(f"Green Taxi - Zero passengers trips: {zero_pass}")
        logger.info(f"Green taxi zero passengers: {zero_pass}")
        
        # Check for 0 miles
        zero_miles = con.execute(
            "SELECT COUNT(*) FROM green_taxi_cleaned WHERE trip_distance = 0"
        ).fetchall()[0][0]
        print(f"Green Taxi - Zero miles trips: {zero_miles}")
        logger.info(f"Green taxi zero miles: {zero_miles}")
        
        # Check for > 100 miles
        over_100 = con.execute(
            "SELECT COUNT(*) FROM green_taxi_cleaned WHERE trip_distance > 100"
        ).fetchall()[0][0]
        print(f"Green Taxi - Trips over 100 miles: {over_100}")
        logger.info(f"Green taxi over 100 miles: {over_100}")
        
        # Check for > 86400 seconds
        over_day = con.execute(
            "SELECT COUNT(*) FROM green_taxi_cleaned WHERE duration_seconds > 86400"
        ).fetchall()[0][0]
        print(f"Green Taxi - Trips over 1 day duration: {over_day}")
        logger.info(f"Green taxi over 1 day: {over_day}")
        
        green_before = con.execute("SELECT COUNT(*) FROM green_taxi").fetchall()[0][0]
        green_after = con.execute("SELECT COUNT(*) FROM green_taxi_cleaned").fetchall()[0][0]
        green_removed = green_before - green_after
        print(f"Green Taxi - Rows before: {green_before:,}, After: {green_after:,}, Removed: {green_removed:,}\n")
        logger.info(f"Green taxi: {green_before} -> {green_after} ({green_removed} removed)")
        
        con.close()
        logger.info("Data cleaning completed successfully")
        print("Cleaning verification complete!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
        if con:
            con.close()

if __name__ == "__main__":
    clean_trips()

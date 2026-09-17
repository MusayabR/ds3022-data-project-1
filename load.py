import duckdb
import os
import logging
import requests
from typing import Tuple
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

def download_parquet_file(url: str, file_name: str) -> bool:
    """Download a parquet file from NYC TLC website."""
    try:
        logger.info(f"Downloading {file_name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(file_name, 'wb') as f:
            f.write(response.content)
        logger.info(f"Successfully downloaded {file_name}")
        return True
    except Exception as e:
        logger.error(f"Error downloading {file_name}: {e}")
        print(f"Error downloading {file_name}: {e}")
        return False

def load_parquet_files() -> None:
    """
    Load NYC taxi trip data for 2024 and vehicle emissions into DuckDB.
    Creates three tables: yellow_taxi, green_taxi, and vehicle_emissions.
    """
    con = None
    
    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")
        
        # Base URL for NYC TLC data
        base_url = "https://d37ciml9hvs7zo.cloudfront.net"
        
        # Months and taxi types
        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        
        # Create yellow taxi table
        logger.info("Creating yellow_taxi table...")
        con.execute("""
            CREATE TABLE IF NOT EXISTS yellow_taxi (
                VendorID INTEGER,
                tpep_pickup_datetime TIMESTAMP,
                tpep_dropoff_datetime TIMESTAMP,
                passenger_count INTEGER,
                trip_distance DOUBLE,
                RatecodeID INTEGER,
                store_and_fwd_flag VARCHAR,
                PULocationID INTEGER,
                DOLocationID INTEGER,
                payment_type INTEGER,
                fare_amount DOUBLE,
                extra DOUBLE,
                mta_tax DOUBLE,
                tip_amount DOUBLE,
                tolls_amount DOUBLE,
                total_amount DOUBLE,
                congestion_surcharge DOUBLE,
                airport_fee DOUBLE,
                pickup_time TIMESTAMP,
                duration_seconds INTEGER
            )
        """)
        logger.info("Created yellow_taxi table")
        
        # Create green taxi table
        logger.info("Creating green_taxi table...")
        con.execute("""
            CREATE TABLE IF NOT EXISTS green_taxi (
                VendorID INTEGER,
                lpep_pickup_datetime TIMESTAMP,
                lpep_dropoff_datetime TIMESTAMP,
                passenger_count INTEGER,
                trip_distance DOUBLE,
                RatecodeID INTEGER,
                store_and_fwd_flag VARCHAR,
                PULocationID INTEGER,
                DOLocationID INTEGER,
                payment_type INTEGER,
                fare_amount DOUBLE,
                extra DOUBLE,
                mta_tax DOUBLE,
                tip_amount DOUBLE,
                tolls_amount DOUBLE,
                total_amount DOUBLE,
                congestion_surcharge DOUBLE,
                ehail_fee DOUBLE,
                pickup_time TIMESTAMP,
                duration_seconds INTEGER
            )
        """)
        logger.info("Created green_taxi table")
        
        # Load vehicle emissions data
        logger.info("Loading vehicle_emissions data...")
        con.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_emissions AS
            SELECT * FROM read_csv_auto('data/vehicle_emissions.csv')
        """)
        logger.info("Loaded vehicle_emissions table")
        
        # Load yellow taxi data for 2024
        logger.info("Loading yellow taxi data for 2024...")
        yellow_loaded = 0
        for month in months:
            try:
                file_url = f"{base_url}/trip%20data/yellow_tripdata_2024-{month}.parquet"
                file_name = f"yellow_tripdata_2024-{month}.parquet"
                
                # Check if file already exists locally
                if not os.path.exists(file_name):
                    if not download_parquet_file(file_url, file_name):
                        logger.warning(f"Skipping month {month} for yellow taxi")
                        continue
                
                # Read and insert data
                con.execute(f"""
                    INSERT INTO yellow_taxi
                    SELECT 
                        VendorID,
                        tpep_pickup_datetime,
                        tpep_dropoff_datetime,
                        passenger_count,
                        trip_distance,
                        RatecodeID,
                        store_and_fwd_flag,
                        PULocationID,
                        DOLocationID,
                        payment_type,
                        fare_amount,
                        extra,
                        mta_tax,
                        tip_amount,
                        tolls_amount,
                        total_amount,
                        congestion_surcharge,
                        airport_fee,
                        tpep_pickup_datetime as pickup_time,
                        CAST(EXTRACT(EPOCH FROM (tpep_dropoff_datetime - tpep_pickup_datetime)) AS INTEGER) as duration_seconds
                    FROM read_parquet('{file_name}')
                """)
                yellow_loaded += 1
                logger.info(f"Successfully loaded yellow taxi data for 2024-{month}")
            except Exception as e:
                logger.error(f"Error loading yellow taxi data for month {month}: {e}")
        
        # Load green taxi data for 2024
        logger.info("Loading green taxi data for 2024...")
        green_loaded = 0
        for month in months:
            try:
                file_url = f"{base_url}/trip%20data/green_tripdata_2024-{month}.parquet"
                file_name = f"green_tripdata_2024-{month}.parquet"
                
                # Check if file already exists locally
                if not os.path.exists(file_name):
                    if not download_parquet_file(file_url, file_name):
                        logger.warning(f"Skipping month {month} for green taxi")
                        continue
                
                # Read and insert data
                con.execute(f"""
                    INSERT INTO green_taxi
                    SELECT 
                        VendorID,
                        lpep_pickup_datetime,
                        lpep_dropoff_datetime,
                        passenger_count,
                        trip_distance,
                        RatecodeID,
                        store_and_fwd_flag,
                        PULocationID,
                        DOLocationID,
                        payment_type,
                        fare_amount,
                        extra,
                        mta_tax,
                        tip_amount,
                        tolls_amount,
                        total_amount,
                        congestion_surcharge,
                        ehail_fee,
                        lpep_pickup_datetime as pickup_time,
                        CAST(EXTRACT(EPOCH FROM (lpep_dropoff_datetime - lpep_pickup_datetime)) AS INTEGER) as duration_seconds
                    FROM read_parquet('{file_name}')
                """)
                green_loaded += 1
                logger.info(f"Successfully loaded green taxi data for 2024-{month}")
            except Exception as e:
                logger.error(f"Error loading green taxi data for month {month}: {e}")
        
        # Output raw row counts
        logger.info("Outputting row counts...")
        
        yellow_count = con.execute("SELECT COUNT(*) FROM yellow_taxi").fetchall()[0][0]
        green_count = con.execute("SELECT COUNT(*) FROM green_taxi").fetchall()[0][0]
        emissions_count = con.execute("SELECT COUNT(*) FROM vehicle_emissions").fetchall()[0][0]
        
        print("\n=== RAW ROW COUNTS ===")
        print(f"Yellow Taxi Trips (Raw): {yellow_count:,}")
        print(f"Green Taxi Trips (Raw): {green_count:,}")
        print(f"Vehicle Emissions Records: {emissions_count:,}")
        print("======================\n")
        
        logger.info(f"Yellow taxi raw count: {yellow_count}")
        logger.info(f"Green taxi raw count: {green_count}")
        logger.info(f"Vehicle emissions count: {emissions_count}")
        logger.info(f"Successfully loaded {yellow_loaded} months of yellow taxi data")
        logger.info(f"Successfully loaded {green_loaded} months of green taxi data")
        
        con.close()
        logger.info("Data loading completed successfully")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
        if con:
            con.close()

if __name__ == "__main__":
    load_parquet_files()
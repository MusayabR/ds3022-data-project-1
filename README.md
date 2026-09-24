# DS3022 Data Project 1

this project loads all the 2024 nyc yellow and green taxi trips into duckdb, cleans them up, figures out how much co2 each trip made, and then looks at which hours/days/weeks/months had the most and least co2.

## how to run it

make a venv and install stuff:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

then just run:

python run_pipeline.py

that runs load.py, clean.py, transform.py and analysis.py in order. each one makes its own log file.

## what each file does

load.py - downloads the 24 parquet files (12 months for yellow and green) and loads them into emissions.duckdb along with the vehicle_emissions csv (8 rows). prints the raw row counts and some stats. i got 41,169,720 yellow rows and 660,218 green rows raw.

clean.py - gets rid of duplicates, trips with 0 passengers, 0 miles, over 100 miles, and trips over 86400 seconds (1 day). then it checks each rule again to make sure the count is 0. after cleaning i had 39,434,399 yellow rows and 617,709 green rows.

transform.py - adds trip_co2_kgs, avg_mph, hour_of_day, day_of_week, week_of_year and month_of_year.

analysis.py - finds the biggest co2 trip and the heaviest/lightest hour, day, week and month for yellow and green. also makes co2_by_month.png.

## what i got

- biggest yellow trip was 37.95 kg of co2 (99.86 miles), biggest green was 34.75 kg (99.28 miles)
- both colors had 5am as the heaviest hour and 6pm as the lightest
- august was the heaviest month for both, and week 35 was the heaviest week
- avg speed came out 11.27 mph for yellow and 15.37 for green, green is faster since its mostly outer boroughs

## stuff i decided

- i only loaded 5 columns since the rest werent needed for anything
- renamed tpep_/lpep_ pickup and dropoff to pickup_time and dropoff_time so yellow and green can use the same code
- reading the parquet files straight from the url kept failing on my mac (ssl errors), so i download them into data/ first and added certifi to fix the certificates
- used ROW_NUMBER() to remove duplicates like we did in class
- added 2 extra cleaning rules: trips where dropoff isnt after pickup (breaks avg_mph) and trips not in 2024 (some had dates from 2008 and 2025)
- the co2 number comes from the vehicle_emissions table, its not hard coded
- the plot uses a log scale because yellow is way bigger than green and green looked flat otherwise
- hours are 0-23, days are 0 = sunday to 6 = saturday, and weeks are iso weeks so dec 30-31 count as week 1

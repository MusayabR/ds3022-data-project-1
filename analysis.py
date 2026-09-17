import duckdb
import logging
import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='analysis.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

def analyze_trips() -> None:
    """
    Perform analysis on transformed taxi trip data:
    1. Find largest CO2 producing trip for YELLOW and GREEN
    2. Find most/least carbon heavy hours of day
    3. Find most/least carbon heavy days of week
    4. Find most/least carbon heavy weeks of year
    5. Find most/least carbon heavy months of year
    6. Generate time-series plot of CO2 by month
    """
    con = None
    
    try:
        # Connect to DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")
        
        print("\n" + "="*60)
        print("NYC TAXI CO2 ANALYSIS - 2024")
        print("="*60 + "\n")
        
        # 1. Largest CO2 producing trip
        logger.info("Finding largest CO2 producing trips...")
        print("1. LARGEST CO2 PRODUCING TRIP")
        print("-" * 40)
        
        yellow_max = con.execute("""
            SELECT 
                trip_distance,
                duration_seconds,
                trip_co2_kgs,
                pickup_time
            FROM yellow_taxi_transformed
            ORDER BY trip_co2_kgs DESC
            LIMIT 1
        """).fetchall()
        
        if yellow_max:
            row = yellow_max[0]
            print(f"YELLOW: {row[3]} | Distance: {row[0]} miles | Duration: {row[1]}s | CO2: {row[2]} kg")
            logger.info(f"Largest yellow trip CO2: {row[2]} kg")
        
        green_max = con.execute("""
            SELECT 
                trip_distance,
                duration_seconds,
                trip_co2_kgs,
                pickup_time
            FROM green_taxi_transformed
            ORDER BY trip_co2_kgs DESC
            LIMIT 1
        """).fetchall()
        
        if green_max:
            row = green_max[0]
            print(f"GREEN:  {row[3]} | Distance: {row[0]} miles | Duration: {row[1]}s | CO2: {row[2]} kg")
            logger.info(f"Largest green trip CO2: {row[2]} kg")
        
        print()
        
        # 2. Most/least carbon heavy hours
        logger.info("Finding most/least carbon heavy hours...")
        print("2. MOST/LEAST CARBON HEAVY HOURS (Avg CO2 per trip)")
        print("-" * 40)
        
        yellow_hours = con.execute("""
            SELECT 
                hour_of_day,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM yellow_taxi_transformed
            GROUP BY hour_of_day
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("YELLOW:")
        print(f"  Most carbon heavy hour: {yellow_hours[0][0]}:00 ({yellow_hours[0][1]} kg avg)")
        print(f"  Least carbon heavy hour: {yellow_hours[-1][0]}:00 ({yellow_hours[-1][1]} kg avg)")
        logger.info(f"Yellow most heavy hour: {yellow_hours[0][0]} ({yellow_hours[0][1]} kg)")
        logger.info(f"Yellow least heavy hour: {yellow_hours[-1][0]} ({yellow_hours[-1][1]} kg)")
        
        green_hours = con.execute("""
            SELECT 
                hour_of_day,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM green_taxi_transformed
            GROUP BY hour_of_day
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("GREEN:")
        print(f"  Most carbon heavy hour: {green_hours[0][0]}:00 ({green_hours[0][1]} kg avg)")
        print(f"  Least carbon heavy hour: {green_hours[-1][0]}:00 ({green_hours[-1][1]} kg avg)")
        logger.info(f"Green most heavy hour: {green_hours[0][0]} ({green_hours[0][1]} kg)")
        logger.info(f"Green least heavy hour: {green_hours[-1][0]} ({green_hours[-1][1]} kg)")
        
        print()
        
        # 3. Most/least carbon heavy days of week
        logger.info("Finding most/least carbon heavy days of week...")
        print("3. MOST/LEAST CARBON HEAVY DAYS OF WEEK (Avg CO2 per trip)")
        print("-" * 40)
        
        yellow_days = con.execute("""
            SELECT 
                day_of_week,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM yellow_taxi_transformed
            GROUP BY day_of_week
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("YELLOW:")
        print(f"  Most carbon heavy day: {yellow_days[0][0]} ({yellow_days[0][1]} kg avg)")
        print(f"  Least carbon heavy day: {yellow_days[-1][0]} ({yellow_days[-1][1]} kg avg)")
        logger.info(f"Yellow most heavy day: {yellow_days[0][0]} ({yellow_days[0][1]} kg)")
        logger.info(f"Yellow least heavy day: {yellow_days[-1][0]} ({yellow_days[-1][1]} kg)")
        
        green_days = con.execute("""
            SELECT 
                day_of_week,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM green_taxi_transformed
            GROUP BY day_of_week
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("GREEN:")
        print(f"  Most carbon heavy day: {green_days[0][0]} ({green_days[0][1]} kg avg)")
        print(f"  Least carbon heavy day: {green_days[-1][0]} ({green_days[-1][1]} kg avg)")
        logger.info(f"Green most heavy day: {green_days[0][0]} ({green_days[0][1]} kg)")
        logger.info(f"Green least heavy day: {green_days[-1][0]} ({green_days[-1][1]} kg)")
        
        print()
        
        # 4. Most/least carbon heavy weeks
        logger.info("Finding most/least carbon heavy weeks...")
        print("4. MOST/LEAST CARBON HEAVY WEEKS (Avg CO2 per trip)")
        print("-" * 40)
        
        yellow_weeks = con.execute("""
            SELECT 
                week_of_year,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM yellow_taxi_transformed
            GROUP BY week_of_year
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("YELLOW:")
        print(f"  Most carbon heavy week: Week {yellow_weeks[0][0]} ({yellow_weeks[0][1]} kg avg)")
        print(f"  Least carbon heavy week: Week {yellow_weeks[-1][0]} ({yellow_weeks[-1][1]} kg avg)")
        logger.info(f"Yellow most heavy week: {yellow_weeks[0][0]} ({yellow_weeks[0][1]} kg)")
        logger.info(f"Yellow least heavy week: {yellow_weeks[-1][0]} ({yellow_weeks[-1][1]} kg)")
        
        green_weeks = con.execute("""
            SELECT 
                week_of_year,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM green_taxi_transformed
            GROUP BY week_of_year
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("GREEN:")
        print(f"  Most carbon heavy week: Week {green_weeks[0][0]} ({green_weeks[0][1]} kg avg)")
        print(f"  Least carbon heavy week: Week {green_weeks[-1][0]} ({green_weeks[-1][1]} kg avg)")
        logger.info(f"Green most heavy week: {green_weeks[0][0]} ({green_weeks[0][1]} kg)")
        logger.info(f"Green least heavy week: {green_weeks[-1][0]} ({green_weeks[-1][1]} kg)")
        
        print()
        
        # 5. Most/least carbon heavy months
        logger.info("Finding most/least carbon heavy months...")
        print("5. MOST/LEAST CARBON HEAVY MONTHS (Avg CO2 per trip)")
        print("-" * 40)
        
        yellow_months = con.execute("""
            SELECT 
                month_of_year,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM yellow_taxi_transformed
            GROUP BY month_of_year
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        
        print("YELLOW:")
        print(f"  Most carbon heavy month: {month_names[int(yellow_months[0][0])]} ({yellow_months[0][1]} kg avg)")
        print(f"  Least carbon heavy month: {month_names[int(yellow_months[-1][0])]} ({yellow_months[-1][1]} kg avg)")
        logger.info(f"Yellow most heavy month: {month_names[int(yellow_months[0][0])]} ({yellow_months[0][1]} kg)")
        logger.info(f"Yellow least heavy month: {month_names[int(yellow_months[-1][0])]} ({yellow_months[-1][1]} kg)")
        
        green_months = con.execute("""
            SELECT 
                month_of_year,
                ROUND(AVG(trip_co2_kgs)::NUMERIC, 2) as avg_co2
            FROM green_taxi_transformed
            GROUP BY month_of_year
            ORDER BY avg_co2 DESC
        """).fetchall()
        
        print("GREEN:")
        print(f"  Most carbon heavy month: {month_names[int(green_months[0][0])]} ({green_months[0][1]} kg avg)")
        print(f"  Least carbon heavy month: {month_names[int(green_months[-1][0])]} ({green_months[-1][1]} kg avg)")
        logger.info(f"Green most heavy month: {month_names[int(green_months[0][0])]} ({green_months[0][1]} kg)")
        logger.info(f"Green least heavy month: {month_names[int(green_months[-1][0])]} ({green_months[-1][1]} kg)")
        
        print()
        
        # 6. Generate time-series plot
        logger.info("Generating time-series plot...")
        print("6. GENERATING CO2 BY MONTH PLOT")
        print("-" * 40)
        
        # Get monthly totals for plotting
        yellow_monthly = con.execute("""
            SELECT 
                month_of_year,
                ROUND(SUM(trip_co2_kgs)::NUMERIC, 0) as total_co2
            FROM yellow_taxi_transformed
            GROUP BY month_of_year
            ORDER BY month_of_year
        """).fetchall()
        
        green_monthly = con.execute("""
            SELECT 
                month_of_year,
                ROUND(SUM(trip_co2_kgs)::NUMERIC, 0) as total_co2
            FROM green_taxi_transformed
            GROUP BY month_of_year
            ORDER BY month_of_year
        """).fetchall()
        
        # Create DataFrame for plotting
        months = [int(row[0]) for row in yellow_monthly]
        yellow_co2 = [float(row[1]) for row in yellow_monthly]
        green_co2 = [float(row[1]) for row in green_monthly]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(months, yellow_co2, marker='o', label='Yellow Taxi', linewidth=2, markersize=8)
        plt.plot(months, green_co2, marker='s', label='Green Taxi', linewidth=2, markersize=8)
        
        plt.xlabel('Month of 2024', fontsize=12, fontweight='bold')
        plt.ylabel('Total CO2 Emissions (kg)', fontsize=12, fontweight='bold')
        plt.title('NYC Taxi CO2 Emissions by Month - 2024', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xticks(months, [month_names[m] for m in months])
        
        # Format y-axis to show numbers in millions/thousands
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
        
        plt.tight_layout()
        plt.savefig('co2_by_month.png', dpi=300, bbox_inches='tight')
        print("Plot saved as 'co2_by_month.png'")
        logger.info("Plot saved as co2_by_month.png")
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60 + "\n")
        
        con.close()
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
        if con:
            con.close()

if __name__ == "__main__":
    analyze_trips()
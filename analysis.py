import duckdb
import logging
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('analysis.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# DuckDB DAYOFWEEK: 0 = Sunday ... 6 = Saturday
DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def largest_trip(con, color):
    """Single largest co2 trip of the year."""
    row = con.execute(f"""
        SELECT pickup_time, trip_distance, trip_co2_kgs
        FROM {color}_trips
        ORDER BY trip_co2_kgs DESC LIMIT 1
    """).fetchone()
    logger.info(f"{color.upper()} largest carbon trip: {row[2]:.2f} kg CO2 "
                f"({row[1]} miles, pickup {row[0]})")


def heavy_and_light(con, color, column, label):
    """Heaviest and lightest average co2 for one time column."""
    query = f"""
        SELECT {column}, AVG(trip_co2_kgs) AS avg_co2
        FROM {color}_trips
        GROUP BY {column}
        ORDER BY avg_co2 {{}} LIMIT 1
    """
    heavy = con.execute(query.format("DESC")).fetchone()
    light = con.execute(query.format("ASC")).fetchone()

    # swap numbers for names on day and month
    h, l = heavy[0], light[0]
    if column == "day_of_week":
        h, l = DAYS[h], DAYS[l]
    elif column == "month_of_year":
        h, l = MONTHS[h - 1], MONTHS[l - 1]

    logger.info(f"{color.upper()} most carbon heavy {label}: {h} ({heavy[1]:.3f} kg avg)")
    logger.info(f"{color.upper()} most carbon light {label}: {l} ({light[1]:.3f} kg avg)")


def make_plot(con):
    """Line plot of total co2 per month, yellow vs green."""
    for color, line_color in [("yellow", "gold"), ("green", "green")]:
        df = con.execute(f"""
            SELECT month_of_year, SUM(trip_co2_kgs) AS total_co2
            FROM {color}_trips
            GROUP BY month_of_year
            ORDER BY month_of_year
        """).df()
        plt.plot(df["month_of_year"], df["total_co2"], marker="o",
                 color=line_color, label=f"{color.title()} taxi")

    plt.xticks(range(1, 13), MONTHS)
    plt.title("Total CO2 by Month, 2024")
    plt.xlabel("Month")
    plt.ylabel("CO2 (kg)")
    plt.yscale("log")  # yellow is much bigger than green
    plt.legend()
    plt.tight_layout()
    plt.savefig("co2_by_month.png")
    logger.info("plot saved to co2_by_month.png")


def run_analysis():
    """Answer the analysis questions for both cab types."""
    con = None

    try:
        con = duckdb.connect(database='emissions.duckdb', read_only=True)
        logger.info("Connected to DuckDB instance")

        for color in ["yellow", "green"]:
            largest_trip(con, color)
            heavy_and_light(con, color, "hour_of_day", "hour of day")
            heavy_and_light(con, color, "day_of_week", "day of week")
            heavy_and_light(con, color, "week_of_year", "week of year")
            heavy_and_light(con, color, "month_of_year", "month of year")

        make_plot(con)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    run_analysis()
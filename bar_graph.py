import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine


def plot_delays_by_airline():
    engine = create_engine('sqlite:///flights.sqlite3')

    query = """
    SELECT 
        airlines.airline AS AIRLINE, 
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    JOIN airlines ON flights.airline = airlines.id
    GROUP BY airlines.airline
    """

    df = pd.read_sql(query, engine)
    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100

    plt.figure(figsize=(12,6))
    sns.barplot(x='AIRLINE', y='percent_delayed', data=df)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Percentage of Delayed Flights')
    plt.title('Percentage of Delayed Flights by Airline')
    plt.tight_layout()
    plt.show()


def plot_delays_by_hour():
    engine = create_engine('sqlite:///flights.sqlite3')

    query = """
    SELECT 
        CAST(substr(flights.scheduled_departure, 1, 2) AS INTEGER) AS hour,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    GROUP BY hour
    ORDER BY hour
    """

    df = pd.read_sql(query, engine)

    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100

    plt.figure(figsize=(12,6))
    sns.barplot(x='hour', y='percent_delayed', data=df, palette="YlGnBu")
    plt.ylabel('Percentage of Delayed Flights')
    plt.xlabel('Hour of Day')
    plt.title('Percentage of Delayed Flights by Hour of Day')
    plt.xticks(range(24))  # Hours from 0 to 23
    plt.colorbar = False  # no colorbar needed for bar chart
    plt.tight_layout()
    plt.show()


def plot_heatmap_of_routes():
    engine = create_engine('sqlite:///flights.sqlite3')

    query = """
    SELECT 
        flights.origin_airport AS origin,
        flights.destination_airport AS destination,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    GROUP BY origin, destination
    """

    df = pd.read_sql(query, engine)

    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100

    # Pivot the data for heatmap
    pivot_df = df.pivot(index='origin', columns='destination', values='percent_delayed')

    plt.figure(figsize=(9,8))
    sns.heatmap(pivot_df, cmap="Reds", linewidths=0.5)
    plt.title('Heatmap: % Delayed Flights by Route (Origin → Destination)')
    plt.ylabel('Origin Airport')
    plt.xlabel('Destination Airport')
    plt.tight_layout()
    plt.show()
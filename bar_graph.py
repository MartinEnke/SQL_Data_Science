import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import folium
import webbrowser


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



def plot_map_of_routes():
    engine = create_engine('sqlite:///flights.sqlite3')

    # Get delay data
    query = """
    SELECT 
        flights.origin_airport AS origin,
        flights.destination_airport AS destination,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    GROUP BY origin, destination
    """

    df_routes = pd.read_sql(query, engine)
    df_routes['percent_delayed'] = (df_routes['delayed_flights'] / df_routes['total_flights']) * 100

    # Get airport coordinates
    query_airports = """
    SELECT IATA_CODE, LATITUDE, LONGITUDE
    FROM airports
    WHERE IATA_CODE IS NOT NULL
    """
    df_airports = pd.read_sql(query_airports, engine)
    airport_coords = df_airports.set_index('IATA_CODE')[['LATITUDE', 'LONGITUDE']].to_dict('index')

    # Create the base map
    flight_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # Center of USA

    # Draw routes
    for idx, row in df_routes.iterrows():
        origin = row['origin']
        dest = row['destination']
        delay_percent = row['percent_delayed']

        if origin not in airport_coords or dest not in airport_coords:
            continue  # Skip if coordinates missing

        # Only show meaningful delayed routes
        if delay_percent <= 30:
            continue  # Skip routes with low delay

        origin_coords = (float(airport_coords[origin]['LATITUDE']), float(airport_coords[origin]['LONGITUDE']))
        dest_coords = (float(airport_coords[dest]['LATITUDE']), float(airport_coords[dest]['LONGITUDE']))

        # Color logic (simpler now because only bad delays shown)
        if delay_percent > 50:
            color = 'red'
        else:
            color = 'orange'

        folium.PolyLine(
            locations=[origin_coords, dest_coords],
            color=color,
            weight=1 + delay_percent / 40,  # Thicker for worse delay
            opacity=0.5,
            tooltip=f"{origin} → {dest}: {delay_percent:.1f}% delayed"
        ).add_to(flight_map)

    # Save and display
    flight_map.save('delayed_routes_map.html')
    webbrowser.open('delayed_routes_map.html')
    print("Map saved as 'delayed_routes_map.html'. Open it in your browser!")

from flask import Flask, jsonify, Response
import pandas as pd
from sqlalchemy import create_engine


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Create a connection to your database
engine = create_engine('sqlite:///flights.sqlite3')


@app.route('/')
def home():
    """
    Returns a JSON welcome message for the Flight Analyzer API.
    """
    return jsonify({
        "message": "Welcome to the Flight Delay Analyzer API!",
        "available_endpoints": {
            "/delays_by_airline": "Get % of delayed flights by airline",
            "/delays_by_hour": "Get % of delayed flights by hour"
        },
        "status": "running"
    })

@app.route('/delays_by_airline')
def delays_by_airline():
    """
    API endpoint: Returns percentage of delayed flights per airline as JSON
    """
    query = """
    SELECT 
        airlines.airline AS airline,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    JOIN airlines ON flights.airline = airlines.id
    GROUP BY airlines.airline
    """

    df = pd.read_sql(query, engine)
    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100

    # Convert to list of dictionaries
    result = df[['airline', 'percent_delayed']].to_dict(orient='records')

    return jsonify(result)


@app.route('/delays_by_hour')
def delays_by_hour():
    """
    API endpoint: Returns percentage of delayed flights by hour of day as JSON
    """
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

    # Convert to list of dictionaries
    result = df[['hour', 'percent_delayed']].to_dict(orient='records')

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5025, debug=True)
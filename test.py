from flask import Flask, request, render_template, jsonify
import pandas as pd
from geopy.distance import geodesic

app = Flask(__name__)

# Read data
airports_cols = ['Airport ID','City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone', 'Type', 'Source']
routes_cols = ['Airline', 'Airline ID', 'Source airport', 'Source airport ID', 'Destination airport', 'Destination airport ID', 'Codeshare', 'Stops', 'Equipment']
airports = pd.read_csv('data/airports.csv', names=airports_cols, header=None, index_col=None, na_values='\\N')
routes = pd.read_csv('data/routes.csv', names=routes_cols, header=None, index_col=None, na_values='\\N')
source_airports = airports[['IATA', 'Latitude', 'Longitude']].rename(columns={'IATA': 'Source airport'})
destination_airports = airports[['IATA', 'Latitude', 'Longitude']].rename(columns={'IATA': 'Destination airport'})

routes_with_source = pd.merge(routes, source_airports, on='Source airport', how='left')
routes_with_coordinates = pd.merge(routes_with_source, destination_airports, on='Destination airport', how='left')

# Remove entries with null values for coordinates
routes_with_coordinates = routes_with_coordinates.dropna(subset=['Latitude_x', 'Longitude_x', 'Latitude_y', 'Longitude_y'])

# Calculate distance
def calculate_distance(row):
    source = (row['Latitude_x'], row['Longitude_x'])
    dest = (row['Latitude_y'], row['Longitude_y'])
    return geodesic(source, dest).kilometers

routes_with_coordinates['Distance'] = routes_with_coordinates.apply(calculate_distance, axis=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_route', methods=['GET'])
def get_route():
    source = request.args.get('source')
    destination = request.args.get('destination')
    result = routes_with_coordinates[(routes_with_coordinates['Source airport'] == source) & (routes_with_coordinates['Destination airport'] == destination)]
    # Replace NaN values with None before converting to JSON
    result_json = result.where(pd.notnull(result), None).to_dict(orient='records')
    print(result)
    return jsonify(result_json)
   # return jsonify(result.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

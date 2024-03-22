# Import necessary libraries
import html
import json
from flask import Flask, request, jsonify, render_template
import csv
import math

from amadeus import Client, ResponseError
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize Amadeus client
amadeus = Client(
    client_id='BxsFW8YgIcfqCGSiwk1GPvcJnttW266T',
    client_secret='WnFBmc33acG9bWHf'
)

# Helper function to get flight offers


def get_flight_offers(origin, destination):
    # Retrieves current date
    date = datetime.today().strftime('%Y-%m-%d')
    flight_offers = []

    try:
        # Finds prices by different airlines from point A to B at a specific date
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            nonStop='true',
            currencyCode='SGD',
            max=5
        )

        # Extract airline code and respective prices from each flight offer
        for offer in response.data:
            flight_offers.append({
                "carrierCode": offer['itineraries'][0]['segments'][0]['carrierCode'],
                "priceSGD": offer['price']['total']
            })

    except ResponseError as error:
        print(error)

    return flight_offers

# Helper function to calculate distance between two points given their latitude and longitude


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate differences in latitude and longitude
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula to calculate distance
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * \
        math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

# Helper function to read airports data from CSV file


def read_airports_from_csv(filename):
    airports = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            country = row[2]
            iata_code = row[3]
            lat = float(row[4])
            lon = float(row[5])
            airports[iata_code] = {'country': country, 'coords': (lat, lon)}
    return airports

# Helper function to get country coordinate from country name


def get_country_coordinate_from_country(country):
    coordinate = None

    with open('data/airports_Asia.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[3].strip().lower() == country.lower():  # Check if the country matches
                # Save the coordinates
                coordinate = (float(row[4]), float(row[5]))
                print(f"{country} Coordinate:", coordinate)
                return coordinate
    return coordinate

# Helper function to construct graph dictionary representing airport connections


def construct_graph(airports):
    graph = {}
    for origin_iata, origin_data in airports.items():
        origin_country = origin_data['country']

        connections = []
        for dest_iata, dest_data in airports.items():
            if origin_iata != dest_iata and origin_country != dest_data['country']:
                # Calculate distance between airports
                origin_coords = origin_data['coords']
                dest_coords = dest_data['coords']

                distance = calculate_distance(
                    origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                # Store destination and its distance
                connections.append((dest_iata, distance))
        # Sort connections based on distance
        connections.sort(key=lambda x: x[1])  # Sort based on distance
        graph[origin_iata] = [conn[0]
                              # Store only the airport IATA codes
                              for conn in connections]
    return graph

# Helper function to perform Depth-First Search (DFS) to generate flight routes


def dfs(graph, current, destination, max_layovers, path, routes, max_routes, airports):
    if len(path) - 1 > max_layovers + 1 or len(routes) >= max_routes:
        return
    if current == destination:
        routes.append(path)
        return
    for neighbor in graph.get(current, []):
        if neighbor not in path:
            dfs(graph, neighbor, destination, max_layovers,
                path + [neighbor], routes, max_routes, airports)

# Helper function to get flight routes


def get_flight_routes(origin, destination, max_layovers, airports):
    # Construct the graph based on the distances between airports and their countries
    graph = construct_graph(airports)

    # Set max routes to 10. Can be changed accordingly
    max_routes = 10

    # Empty array which will then be filled with generated routes using DFS algorithm
    routes = []

    # Check for direct flight
    if destination in graph.get(origin, []):
        routes.append([origin, destination])

    # If max layovers is 0, only direct flight is possible
    if max_layovers == 0:
        direct_routes = []
        if routes:
            for route in routes:
                direct_routes.append(route)
            return direct_routes
        else:
            return []

    else:
        dfs(graph, origin, destination, max_layovers,
            [origin], routes, max_routes, airports)

        if routes:
            result_routes = []
            for route in routes:
                # Calculate the distance of the generated routes
                total_distance = 0
                for i in range(len(route) - 1):
                    origin_iata = route[i]
                    dest_iata = route[i + 1]
                    origin_coords = airports[origin_iata]['coords']
                    # Store source coordinate
                    dest_coords = origin_coords[0], origin_coords[1]
                    distance = calculate_distance(
                        origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                    total_distance += distance

                # Append total distance to the route
                route.append(total_distance)

                # Append the route to result_routes
                result_routes.append(route)

            return result_routes
        else:
            return []

# Helper function to calculate flyover coordinates for each route


def calculate_flyover_coordinates(route, airports):
    flyover_coordinates = []
    for i in range(1, len(route) - 2):
        airport_code = route[i]
        coordinates = airports[airport_code]['coords']
        flyover_coordinates.append(coordinates)
    return flyover_coordinates

# Route to handle the get_route request


@app.route('/get_route', methods=['GET'])
def get_route():
    origin = request.args.get('source').upper()
    destination = request.args.get('destination').upper()
    max_layovers = int(request.args.get('layover'))

    # Get source and destination coordinates
    source_coordinate = get_country_coordinate_from_country(origin)
    dest_coordinate = get_country_coordinate_from_country(destination)

    filename = 'data/airports_Asia.csv'
    airports = read_airports_from_csv(filename)

    graph = construct_graph(airports)

    routes_with_flyover = []
    flight_routes = get_flight_routes(
        origin, destination, max_layovers, airports=airports)

    for route in flight_routes:
        flyover_coordinates = calculate_flyover_coordinates(route, airports)
        total_distance = 0
        for i in range(len(route) - 1):
            origin_iata = route[i]
            dest_iata = route[i + 1]
            if origin_iata != dest_iata:  # Check if origin and destination are different
                origin_coords = airports[origin_iata]['coords']
                dest_coords = dest_coordinate[0], dest_coordinate[1]
                distance = calculate_distance(
                    origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                total_distance += distance

            print(f"Distance from {origin_iata} to {dest_iata}: {distance} km")
        print(f"Total distance for route {route}: {total_distance} km")

        routes_with_flyover.append({
            'route': route,
            'flyover_coordinates': flyover_coordinates,
            # Use default coordinates if dest_coordinate is None
            'dest_coordinate': dest_coordinate if dest_coordinate else (0, 0),
            "sourceCoordinate": source_coordinate,
            "total_distance": total_distance
        })

    print(routes_with_flyover)
    print(source_coordinate)

    return jsonify({"routes": routes_with_flyover, "sourceCoordinate": source_coordinate})

# Route to render the index.html template


@app.route('/')
def index():
    return render_template('index.html')

# Route to handle OneMap view


@app.route('/OneMap', methods=['GET', 'POST'])
def OneMap():
    if request.method == 'POST':
        # Decode HTML entities
        source_coordinate = html.unescape(
            request.form.get('Source', default="Not Stated"))
        flyover_coordinates = html.unescape(
            request.form.get('Flyover', default="Not Stated"))
        dest_coordinate = html.unescape(
            request.form.get('Dest', default="Not Stated"))
        FlightRoutes = request.form.get('FlightRoutes', default="Not Stated")

        return render_template('oneMap.html',
                               source_coordinate=source_coordinate,
                               flyover_coordinates=flyover_coordinates,
                               dest_coordinate=dest_coordinate,
                               FlightRoutes=FlightRoutes
                               )
    else:
        return render_template('oneMap.html')


# Main method to run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

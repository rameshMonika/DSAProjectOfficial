from amadeus import Client, ResponseError
from datetime import datetime
import csv
import math

# Initialize Amadeus client
amadeus = Client(
    client_id='BxsFW8YgIcfqCGSiwk1GPvcJnttW266T',
    client_secret='WnFBmc33acG9bWHf'
)

# Calculates the distance between two points given their latitude and longitude
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
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

# Data manipulation to retrieve relevant information from csv file
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

# Construct the graph dictionary - the airport locations becomes a node in the graph
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
                distance = calculate_distance(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                connections.append((dest_iata, distance))  # Store destination and its distance
        # Sort connections based on distance
        connections.sort(key=lambda x: x[1])  # Sort based on distance
        graph[origin_iata] = [conn[0] for conn in connections]  # Store only the airport IATA codes
    return graph

# Retrieve flight prices for a given route
def get_flight_prices(origin, destination, response_data):
    for itinerary in response_data:
        segments = itinerary['itineraries'][0]['segments']
        for segment in segments:
            if segment['departure']['iataCode'] == origin and segment['arrival']['iataCode'] == destination:
                return float(itinerary['price']['total'])
    return 0  # Return 0 if flight price is not available

# Check if a flight offer exists for a given route segment in the response data
def check_flight_offer(origin, destination, response_data):
    for itinerary in response_data:
        segments = itinerary['itineraries'][0]['segments']
        for segment in segments:
            if segment['departure']['iataCode'] == origin and segment['arrival']['iataCode'] == destination:
                return True
    return False

# DFS algorithm to generate possible flight routes including layover flights
def dfs(graph, origin, destination, max_layovers, path, response_data, visited=None):
    if visited is None:
        visited = set()
    visited.add(origin)

    if len(path) - 1 > max_layovers + 1:
        return []

    if origin == destination:
        return [path]

    routes = []

    for neighbor in graph.get(origin, []):
        if neighbor not in visited:
            new_route = path + [neighbor]
            if check_flight_offer(origin, neighbor, response_data):
                routes.extend(dfs(graph, neighbor, destination, max_layovers, new_route, response_data, visited))
            else:
                new_route.append(destination)
                if check_flight_offer(neighbor, destination, response_data):
                    routes.append(new_route)

    visited.remove(origin)
    return routes

# Print flight routes with their total distances, sorted by cheapest flight
def print_flight_routes(direct_route, routes, response_data):

    #Direct Flight  
    print("Routes from", origin, "to", destination)
    print(f"{direct_route}")
    total_distance = calculate_distance(*airports[origin]['coords'], *airports[destination]['coords'])
    total_price = get_flight_prices(origin, destination, response_data)
    print(f"Total Distance: {round(total_distance, 2)} km")
    print(f"Total Price (SGD): {round(total_price, 2)}")
    print()

    # Sort routes by total price
    routes.sort(key=lambda route: sum(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1)))

    #Layover Flights
    for i, route in enumerate(routes[:10], start=1):  # Limit to only 10 routes
        total_distance = sum(calculate_distance(*airports[route[j]]['coords'], *airports[route[j+1]]['coords']) for j in range(len(route) - 1))
        total_price = sum(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1))
        print(f"{route}")
        print(f"Total Distance: {round(total_distance, 2)} km")
        print(f"Total Price (SGD): {round(total_price, 2)}")
        print()

# User input for origin and destination
filename = 'airports_Asia.csv'

# Read airports with their latitude and longitude coordinates and country
airports = read_airports_from_csv(filename)

# Construct the graph based on the distances between airports and their countries
graph = construct_graph(airports)

# User input for origin and destination
origin = input("Enter origin IATA code: ")
destination = input("Enter destination IATA code: ")
date = input("Enter departure date (YYYY-MM-DD): ")

# Retrieve flight data for the given origin-destination pair
response = amadeus.shopping.flight_offers_search.get(
    originLocationCode=origin,
    destinationLocationCode=destination,
    departureDate=date,
    adults=1,
    currencyCode='SGD',
    nonStop='false',
    max=50
)

response_data = response.data

# Empty array which will then be filled with generated routes using DFS algorithm
routes = []

# Check if flight data is available
if response_data:
    # Check for direct flight
    direct_route = [origin, destination] if destination in graph.get(origin, []) else None
    
    # Use DFS to generate flight routes
    routes = dfs(graph, origin, destination, 2, [origin], response_data)

    # Print flight routes
    print_flight_routes(direct_route, routes, response_data)
else:
    print("No flight data available.")
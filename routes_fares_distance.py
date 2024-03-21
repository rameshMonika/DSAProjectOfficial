from amadeus import Client, ResponseError
from datetime import datetime
import csv
import math
import heapq

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
        connections = {}  # Change from list to dictionary
        for dest_iata, dest_data in airports.items():
            if origin_iata != dest_iata and origin_country != dest_data['country']:
                # Calculate distance between airports
                origin_coords = origin_data['coords']
                dest_coords = dest_data['coords']
                distance = calculate_distance(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                connections[dest_iata] = distance  # Store destination and its distance
        graph[origin_iata] = connections
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

# Print flight routes with their total distances
def print_flight_routes(direct_route, routes, response_data):
    if direct_route:
        print("Direct Flight Route from", origin, "to", destination)
        print(f"Route: {direct_route}")
        total_distance = calculate_distance(*airports[origin]['coords'], *airports[destination]['coords'])
        total_price = get_flight_prices(origin, destination, response_data)
        print(f"Total Distance: {total_distance} km")
        print(f"Total Price (SGD): {total_price}")
        print()

    print("Indirect Flight Routes from", origin, "to", destination)
    for i, route in enumerate(routes[:10], start=1):  # Limit to only 10 routes
        total_distance = sum(calculate_distance(*airports[route[j]]['coords'], *airports[route[j+1]]['coords']) for j in range(len(route) - 1))
        total_price = sum(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1))
        print(f"Route {i}: {route}")
        print(f"Total Distance: {total_distance} km")
        print(f"Total Price (SGD): {total_price}")
        print()


# Dijkstra's algorithm to find shortest path in terms of distance
def dijkstra(graph, origin, destination):
    distances = {airport: float('inf') for airport in graph}
    distances[origin] = 0
    previous = {airport: None for airport in graph}
    priority_queue = [(0, origin)]

    while priority_queue:
        current_distance, current_airport = heapq.heappop(priority_queue)

        if current_distance > distances[current_airport]:
            continue

        for neighbor in graph[current_airport]:
            distance = current_distance + graph[current_airport][neighbor]
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_airport
                heapq.heappush(priority_queue, (distance, neighbor))

    path = []
    airport = destination
    while airport:
        path.append(airport)
        airport = previous[airport]

    return path[::-1], distances[destination]

# Method to get the most optimal route considering both cost and distance
def get_optimal_route(graph, origin, destination, response_data):
    # Use Dijkstra's algorithm to find the shortest path in terms of distance
    shortest_path, shortest_distance = dijkstra(graph, origin, destination)

    # Initialize variables to store optimal route and its total cost
    optimal_route = None
    min_cost = float('inf')

    # Iterate through each possible route
    for i in range(len(shortest_path) - 1):
        current_origin = shortest_path[i]
        current_destination = shortest_path[i + 1]

        # Check if flight offer exists for the current route segment
        if check_flight_offer(current_origin, current_destination, response_data):
            # Calculate total cost for the current route
            total_cost = sum(get_flight_prices(current_origin, current_destination, response_data) 
                             for current_origin, current_destination in zip(shortest_path, shortest_path[1:]))

            # Update optimal route if total cost is lower than current minimum cost
            if total_cost < min_cost:
                optimal_route = shortest_path[i:i + 2]
                min_cost = total_cost

    return optimal_route, min_cost

# User input for origin and destination
filename = 'data/airports_Asia.csv'

# Read airports with their latitude and longitude coordinates and country
airports = read_airports_from_csv(filename)

# Construct the graph based on the distances between airports and their countries
graph = construct_graph(airports)

# User input for origin and destination
origin = input("Enter origin IATA code: ")
destination = input("Enter destination IATA code: ")
date = input("Enter deprature date (YYYY-MM-DD): ")

# Retrieve flight data for the given origin-destination pair
response = amadeus.shopping.flight_offers_search.get(
    originLocationCode=origin,
    destinationLocationCode=destination,
    departureDate=date,
    adults=1,
    currencyCode='SGD',
    nonStop='false',
    max = 50
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
    
    # Calling the function to get the optimal route
    optimal_route, min_cost = get_optimal_route(graph, origin, destination, response_data)
    if optimal_route:
        print("Most Optimal Flight Route from", origin, "to", destination)
        print(f"Optimal Route: {optimal_route}")
        print(f"Total Cost (SGD): {min_cost}")
    else:
        print("No optimal route found.")
        
else:
    print("No flight data available.")
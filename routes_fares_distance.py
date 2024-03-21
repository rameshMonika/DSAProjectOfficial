import heapq
from amadeus import Client
import csv
import math
import datetime

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
        distances = {}
        for dest_iata, dest_data in airports.items():
            if origin_iata != dest_iata and origin_country != dest_data['country']:
                # Calculate distance between airports
                origin_coords = origin_data['coords']
                dest_coords = dest_data['coords']
                distance = calculate_distance(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                distances[dest_iata] = distance
        graph[origin_iata] = distances
    return graph

# Dijkstra's algorithm to find the shortest distance between two airports
def dijkstra(graph, start, end):
    # Initialize distances with infinity for all nodes
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    
    # Priority queue to store nodes and their distances
    pq = [(0, start)]  # (distance, node)
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # If we have already processed this node
        if current_distance > distances[current_node]:
            continue
        
        # Iterate through neighbors of current node
        for neighbor, distance in graph[current_node].items():
            total_distance = current_distance + distance
            # If shorter path found, update distance
            if total_distance < distances[neighbor]:
                distances[neighbor] = total_distance
                heapq.heappush(pq, (total_distance, neighbor))
    
    return distances[end]

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
                # Only append destination if there's a valid flight offer
                if check_flight_offer(neighbor, destination, response_data):
                    updated_routes = dfs(graph, neighbor, destination, max_layovers, new_route, response_data, visited)
                    routes.extend(updated_routes)
                else:
                    # Check if the current neighbor is the destination airport
                    if neighbor == destination:
                        routes.append(new_route)

    visited.remove(origin)
    return routes

# Handles the flight routes with their total distances, sorted by cheapest flight
def print_flight_routes(graph, direct_route, routes, response_data, airports, origin, destination):
    printed_routes = set()  # Set to store printed routes
    direct_data = []
    indirect_data = []

    if direct_route:
        # Sort direct routes by total price
        direct_route.sort(key=lambda route: get_flight_prices(route[0], route[1], response_data))
        direct_data = print_route_info(direct_route, response_data, graph, printed_routes)
        print()
    elif routes:
        # Sort indirect routes by total price
        routes.sort(key=lambda route: min(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1)))

        for i, route in enumerate(routes[:10], start=1):  # Limit to only 10 routes
            if len(route) == 2:  # Check if it's a direct flight route
                continue
            else:
                indirect_flight_info = print_route_info(route, response_data, graph, printed_routes)
                if indirect_flight_info:  # Check if the route was printed
                    indirect_data.extend(indirect_flight_info)
                print()
    else:
        print("No flight routes available.")
    
    return direct_data, indirect_data

# Handles each flight information, calculating the total distance and retrieving associated airline and total price
def print_route_info(route_data, response_data, graph, printed_routes):
    total_distance = sum(dijkstra(graph, route_data[j], route_data[j+1]) for j in range(len(route_data) - 1))
    route_tuple = tuple(route_data)
    direct_flights_data = []
    indirect_flights_data = []

    if route_tuple not in printed_routes:  # Check if route has been printed before
        printed_routes.add(route_tuple)  # Add route to printed routes set

        # Extract unique segment information
        unique_segments = set()
        for itinerary in response_data:
            for segment in itinerary['itineraries'][0]['segments']:
                unique_segments.add((segment['departure']['iataCode'], segment['arrival']['iataCode'], segment['carrierCode'], float(itinerary['price']['total'])))

        # Sort segments by price
        sorted_segments = sorted(unique_segments, key=lambda x: x[3])

        # Direct flight
        if len(route_data) == 2:
            for origin, destination in zip(route_data[:-1], route_data[1:]):
                for segment in sorted_segments:
                    if segment[0] == origin and segment[1] == destination:
                        print(f"Route: [{origin}, {destination}]")
                        print(f"Total Distance: {round(total_distance, 2)} km")
                        print(f"Airline: {segment[2]}")
                        print(f"Total Price (SGD): {segment[3]}")
                        print()
                        direct_flights_data.append(([origin, destination], round(total_distance, 2), segment[2], segment[3]))
            return direct_flights_data

        # Indirect flight        
        elif len(route_data) > 2:
            for i in range(len(route_data) - 1):
                origin, destination = route_data[i], route_data[i+1]
                for segment in sorted_segments:
                    if segment[0] == origin and segment[1] == destination:
                        print(f"Route: {route_data}")
                        print(f"Total Distance: {round(total_distance, 2)} km")
                        print(f"Airline: {segment[2]}")
                        print(f"Total Price (SGD): {segment[3]}")
                        indirect_flights_data.append((route_data, round(total_distance, 2), segment[2], segment[3]))
                        return indirect_flights_data

#Main function
def main():
    # User input for origin and destination
    filename = 'data/airports_Asia.csv'

    # Read airports with their latitude and longitude coordinates and country
    airports = read_airports_from_csv(filename)

    # Construct the graph based on the distances between airports and their countries
    graph = construct_graph(airports)

    # Prompt user to enter valid origin IATA code
    while True:
        origin = input("Enter origin IATA code: ").upper()
        if origin in airports:
            break
        else:
            print("Invalid IATA code. Please try again.")

    # Prompt user to enter valid destination IATA code
    while True:
        destination = input("Enter destination IATA code: ").upper()
        if destination in airports:
            break
        else:
            print("Invalid IATA code. Please try again.")

    # Prompt user to enter a valid departure date (current or future dates)
    while True:
        date_str = input("Enter departure date (YYYY-MM-DD): ")
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            current_date = datetime.datetime.now().date()
            if date >= current_date:
                break
            else:
                print("Invalid date. Please enter a current or future date.")
        except ValueError:
            print("Invalid date format. Please enter date in YYYY-MM-DD format.")

    # Retrieve flight data for the given origin-destination pair
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=origin,
        destinationLocationCode=destination,
        departureDate=date_str,
        adults=1,
        currencyCode='SGD',
        nonStop='false',
        max=50
    )

    response_data = response.data

    # Check if flight data is available
    if response_data:
        # Check for direct flight
        direct_route = [origin, destination] if destination in graph.get(origin, []) else None

        # Prompt user to select between direct or indirect flights
        while True:
            selection = input("Do you want to see direct flights only? (yes/no): ").lower()
            if selection == "yes":
                if direct_route:
                    print_flight_routes(graph, direct_route, [], response_data, airports, origin, destination)
                    break
                else:
                    print("No direct flight available.")
                break
            elif selection == "no":
                routes = dfs(graph, origin, destination, 2, [origin], response_data)
                print_flight_routes(graph, [], routes, response_data, airports, origin, destination)
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    else:
        print("No flight data available.")

# Call the main function
main()
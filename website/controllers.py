from flask import Flask, render_template, request, jsonify
import heapq
import csv
import math
import datetime
from amadeus import Client


# Initialize Amadeus client
amadeus = Client(
    client_id='BxsFW8YgIcfqCGSiwk1GPvcJnttW266T',
    client_secret='WnFBmc33acG9bWHf'
)

# Define helper functions

# Function to calculate the distance between two points given their latitude and longitude
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Function to read airports from a CSV file and return a dictionary
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

# Function to construct the graph dictionary
def construct_graph(airports):
    graph = {}
    for origin_iata, origin_data in airports.items():
        origin_country = origin_data['country']
        distances = {}
        for dest_iata, dest_data in airports.items():
            if origin_iata != dest_iata and origin_country != dest_data['country']:
                origin_coords = origin_data['coords']
                dest_coords = dest_data['coords']
                distance = calculate_distance(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                distances[dest_iata] = distance
        graph[origin_iata] = distances
    return graph

# Function to find the shortest distance between two airports using Dijkstra's algorithm
def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_distance > distances[current_node]:
            continue
        for neighbor, distance in graph[current_node].items():
            total_distance = current_distance + distance
            if total_distance < distances[neighbor]:
                distances[neighbor] = total_distance
                heapq.heappush(pq, (total_distance, neighbor))
    return distances[end]

# Function to check if a flight offer exists for a given route segment in the response data
def check_flight_offer(origin, destination, response_data):
    for itinerary in response_data:
        segments = itinerary['itineraries'][0]['segments']
        for segment in segments:
            if segment['departure']['iataCode'] == origin and segment['arrival']['iataCode'] == destination:
                return True
    return False

# Function to retrieve flight prices for a given route
def get_flight_prices(origin, destination, response_data):
    for itinerary in response_data:
        segments = itinerary['itineraries'][0]['segments']
        for segment in segments:
            if segment['departure']['iataCode'] == origin and segment['arrival']['iataCode'] == destination:
                return float(itinerary['price']['total'])
    return 0

# Function to generate possible flight routes including layover flights using DFS algorithm
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
                if check_flight_offer(neighbor, destination, response_data):
                    updated_routes = dfs(graph, neighbor, destination, max_layovers, new_route, response_data, visited)
                    routes.extend(updated_routes)
                else:
                    if neighbor == destination:
                        routes.append(new_route)
    visited.remove(origin)
    return routes

# Function to print flight routes with their total distances
def print_flight_routes(graph, direct_route, routes, response_data, airports, origin, destination):
    printed_routes = set()
    direct_data = []
    indirect_data = []
    if direct_route:
        direct_route.sort(key=lambda route: get_flight_prices(route[0], route[1], response_data))
        direct_data = print_route_info(direct_route, response_data, graph, printed_routes)
    elif routes:
        routes.sort(key=lambda route: min(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1)))
        for i, route in enumerate(routes[:10], start=1):
            if len(route) == 2:
                continue
            else:
                indirect_flight_info = print_route_info(route, response_data, graph, printed_routes)
              
                if indirect_flight_info:
                    indirect_data.extend(indirect_flight_info)
                   
        print(indirect_data)
   
    return direct_data, indirect_data

# Function to handle each flight information
def print_route_info(route_data, response_data, graph, printed_routes):
    total_distance = sum(dijkstra(graph, route_data[j], route_data[j+1]) for j in range(len(route_data) - 1))
    route_tuple = tuple(route_data)
    direct_flights_data = []
    indirect_flights_data = []
    if route_tuple not in printed_routes:
        printed_routes.add(route_tuple)
        unique_segments = set()
        for itinerary in response_data:
            for segment in itinerary['itineraries'][0]['segments']:
                unique_segments.add((segment['departure']['iataCode'], segment['arrival']['iataCode'], segment['carrierCode'], float(itinerary['price']['total'])))
        sorted_segments = sorted(unique_segments, key=lambda x: x[3])
        if len(route_data) == 2:
            for origin, destination in zip(route_data[:-1], route_data[1:]):
                for segment in sorted_segments:
                    if segment[0] == origin and segment[1] == destination:
                        direct_flights_data.append(([origin, destination], round(total_distance, 2), segment[2], segment[3]))
            return direct_flights_data
        elif len(route_data) > 2:
            for i in range(len(route_data) - 1):
                origin, destination = route_data[i], route_data[i+1]
                for segment in sorted_segments:
                    if segment[0] == origin and segment[1] == destination:
                        indirect_flights_data.append((route_data, round(total_distance, 2), segment[2], segment[3]))
                        return  indirect_flights_data



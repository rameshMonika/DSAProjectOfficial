from flask import Flask, render_template, request, jsonify
import heapq
import csv
import math
import datetime
from amadeus import Client


# Initialize Amadeus client
amadeus = Client(
    client_id='RyTaBkUYFxBCMt1c5SIJX8jqhNqvCq81',
    client_secret='Xpi2SV5TFRBMTshT'
)

weight_discount = 0.4
weight_passengers = 0.6

cached_scores = {}


voucher_data = [
    (3, 200, 10),   # Voucher 1
    (2, 150, 15),   # Voucher 2
    (5, 300, 20),   # Voucher 3
    (4, 250, 25),   # Voucher 4
    (3, 400, 10),   # Voucher 5
    (6, 350, 30),   # Voucher 6
    (2, 200, 20),   # Voucher 7
    (4, 450, 15),   # Voucher 8
    (7, 300, 25),   # Voucher 9
    (5, 350, 30),   # Voucher 10
    (2, 400, 10),   # Voucher 11
    (3, 250, 15),   # Voucher 12
    (4, 200, 25),   # Voucher 13
    (5, 450, 20),   # Voucher 14
    (3, 300, 10),   # Voucher 16
    (7, 400, 15),   # Voucher 17
    (4, 350, 20),   # Voucher 18
    (5, 250, 25),   # Voucher 19
    (6, 200, 30),   # Voucher 20
    (2, 300, 5),    # Voucher 21
    (3, 350, 25),   # Voucher 22
    (4, 200, 20),   # Voucher 23
    (5, 250, 15),   # Voucher 24
    (6, 400, 10),   # Voucher 25
    (3, 450, 30),   # Voucher 26
    (4, 300, 25),   # Voucher 27
    (5, 200, 20),   # Voucher 28
    (6, 350, 15),   # Voucher 29
    (2, 400, 10),   # Voucher 30
    (3, 250, 15),   # Voucher 31
    (4, 200, 25),   # Voucher 32
    (5, 450, 20),   # Voucher 33
    (3, 300, 10),   # Voucher 35
    (7, 400, 15),   # Voucher 36
    (4, 350, 20),   # Voucher 37
    (5, 250, 25),   # Voucher 38
    (6, 200, 30),   # Voucher 39
    (2, 300, 5),    # Voucher 40
    (3, 350, 25),   # Voucher 41
    (4, 200, 20),   # Voucher 42
    (5, 250, 15),   # Voucher 43
    (6, 400, 10),   # Voucher 44
    (3, 450, 30),   # Voucher 45
    (4, 300, 25),   # Voucher 46
    (5, 200, 20),   # Voucher 47
    (6, 350, 15),   # Voucher 48
    (2, 400, 10),   # Voucher 49
    (3, 250, 15),   # Voucher 50
    (4, 200, 25),   # Voucher 51
    (5, 450, 20),   # Voucher 52
    (3, 300, 10),   # Voucher 54
    (7, 400, 15),   # Voucher 55
    (4, 350, 20),   # Voucher 56
    (5, 250, 25),   # Voucher 57
    (6, 200, 30),   # Voucher 58
    (2, 300, 5),    # Voucher 59
    (3, 350, 25),   # Voucher 60
    (4, 200, 20),   # Voucher 61
    (5, 250, 15),   # Voucher 62
    (6, 400, 10),   # Voucher 63
    (3, 450, 30),   # Voucher 64
    (4, 300, 25),   # Voucher 65
    (5, 200, 20),   # Voucher 66
    (6, 350, 15),   # Voucher 67
    (2, 400, 10),   # Voucher 68
    (3, 250, 15),   # Voucher 69
    (4, 200, 25),   # Voucher 70
    (5, 450, 20),   # Voucher 71
    (6, 150, 30),   # Voucher 72
    (3, 300, 10),   # Voucher 73
    (7, 400, 15),   # Voucher 74
    (4, 350, 20),   # Voucher 75
    (5, 250, 25),   # Voucher 76
    (6, 200, 30),   # Voucher 77
    (2, 300, 5),    # Voucher 78
    (3, 350, 25),   # Voucher 79
    (4, 200, 20),   # Voucher 80
    (5, 250, 15),   # Voucher 81
    (6, 400, 10),   # Voucher 82
    (3, 450, 30),   # Voucher 83
    (4, 300, 25),   # Voucher 84
    (5, 200, 20),   # Voucher 85
    (6, 350, 15),   # Voucher 86
    (2, 400, 10),   # Voucher 87
    (3, 250, 15),   # Voucher 88
    (4, 200, 25),   # Voucher 89
    (5, 450, 20),   # Voucher 90
    (3, 300, 10),   # Voucher 92
    (7, 400, 15),   # Voucher 93
    (4, 350, 20),   # Voucher 94
    (5, 250, 25),   # Voucher 95
    (6, 200, 30),   # Voucher 96
    (2, 300, 5),    # Voucher 97
    (3, 350, 25),   # Voucher 98
    (4, 200, 20),   # Voucher 99
    (5, 250, 15),   # Voucher 100
   
]

voucher_data += [
    (6, 400, 10),   # Voucher 101
    (3, 450, 30),   # Voucher 102
    (4, 300, 25),   # Voucher 103
    (5, 200, 20),   # Voucher 104
    (6, 350, 15),   # Voucher 105
    (2, 400, 10),   # Voucher 106
    (3, 250, 15),   # Voucher 107
    (4, 200, 25),   # Voucher 108
    (5, 450, 20),   # Voucher 109
    (3, 300, 10),   # Voucher 111
    (7, 400, 15),   # Voucher 112
    (4, 350, 20),   # Voucher 113
    (5, 250, 25),   # Voucher 114
    (6, 200, 30),   # Voucher 115
    (2, 300, 5),    # Voucher 116
    (3, 350, 25),   # Voucher 117
    (4, 200, 20),   # Voucher 118
    (5, 250, 15),   # Voucher 119
    (6, 400, 10),   # Voucher 120
    (3, 450, 30),   # Voucher 121
    (4, 300, 25),   # Voucher 122
    (5, 200, 20),   # Voucher 123
    (6, 350, 15),   # Voucher 124
    (2, 400, 10),   # Voucher 125
    (3, 250, 15),   # Voucher 126
    (4, 200, 25),   # Voucher 127
    (5, 450, 20),   # Voucher 128
    (3, 300, 10),   # Voucher 130
    (7, 400, 15),   # Voucher 131
    (4, 350, 20),   # Voucher 132
    (5, 250, 25),   # Voucher 133
    (6, 200, 30),   # Voucher 134
    (2, 300, 5),    # Voucher 135
    (3, 350, 25),   # Voucher 136
    (4, 200, 20),   # Voucher 137
    (5, 250, 15),   # Voucher 138
    (6, 400, 10),   # Voucher 139
    (3, 450, 30),   # Voucher 140
    (4, 300, 25),   # Voucher 141
    (5, 200, 20),   # Voucher 142
    (6, 350, 15),   # Voucher 143
    (2, 400, 10),   # Voucher 144
    (3, 250, 15),   # Voucher 145
    (4, 200, 25),   # Voucher 146
    (5, 450, 20),   # Voucher 147
    (3, 300, 10),   # Voucher 149
    (7, 400, 15),   # Voucher 150
    (4, 350, 20),   # Voucher 151
    (5, 250, 25),   # Voucher 152
    (6, 200, 30),   # Voucher 153
    (2, 300, 5),    # Voucher 154
    (3, 350, 25),   # Voucher 155
    (4, 200, 20),   # Voucher 156
    (5, 250, 15),   # Voucher 157
    (6, 400, 10),   # Voucher 158
    (3, 450, 30),   # Voucher 159
    (4, 300, 25),   # Voucher 160
    (5, 200, 20),   # Voucher 161
    (6, 350, 15),   # Voucher 162
    (2, 400, 10),   # Voucher 163
    (3, 250, 15),   # Voucher 164
    (4, 200, 25),   # Voucher 165
    (5, 450, 20),   # Voucher 166
    (3, 300, 10),   # Voucher 168
    (7, 400, 15),   # Voucher 169
    (4, 350, 20),   # Voucher 170
    (5, 250, 25),   # Voucher 171
    (6, 200, 30),   # Voucher 172
    (2, 300, 5),    # Voucher 173
    (3, 350, 25),   # Voucher 174
    (4, 200, 20),   # Voucher 175
    (5, 250, 15),   # Voucher 176
    (6, 400, 10),   # Voucher 177
    (3, 450, 30),   # Voucher 178
    (4, 300, 25),   # Voucher 179
    (5, 200, 20),   # Voucher 180
    (6, 350, 15),   # Voucher 181
    (2, 400, 10),   # Voucher 182
    (3, 250, 15),   # Voucher 183
    (4, 200, 25),   # Voucher 184
    (5, 450, 20),   # Voucher 185
    (3, 300, 10),   # Voucher 187
    (7, 400, 15),   # Voucher 188
    (4, 350, 20),   # Voucher 189
    (5, 250, 25),   # Voucher 190
    (6, 200, 30),   # Voucher 191
    (2, 300, 5),    # Voucher 192
    (3, 350, 25),   # Voucher 193
    (4, 200, 20),   # Voucher 194
    (5, 250, 15),   # Voucher 195
    (6, 400, 10),   # Voucher 196
    (3, 450, 30),   # Voucher 197
    (4, 300, 25),   # Voucher 198
    (5, 200, 20),   # Voucher 199
    (6, 350, 15),   # Voucher 200
]

def get_all_coordinates(route, airports):
    flyover_coordinates = []
    for i in range(1, len(route) - 2):
        airport_code = route[i]
        coordinates = airports[airport_code]["coords"]
        flyover_coordinates.append(coordinates)
    return flyover_coordinates


def getRouteCoordinate(flyover):
    country_codes = []
    for i in range(len(flyover)):
        oneRoute = []
        for j in range(len(flyover[i])):
            oneRoute.append(get_country_coordinate_from_country(flyover[i][j]))
            # print(f"oneRoute[{j}] {oneRoute[j]}")
        country_codes.append(oneRoute)

    return country_codes



def get_country_coordinate_from_country(country):
    coordinate = None

    with open(
        "website/data/airports_Asia.csv", newline="", encoding="utf-8"
    ) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (
                row[3].strip().lower() == country.lower()
            ):  # Check if the country matches
                latitude = float(row[4])
                longitude = float(row[5])
                # Save the coordinates as a tuple
                coordinate = (latitude, longitude)
                # print(f"{country} Coordinate:", coordinate)
                return coordinate
    return coordinate


def getRouteCoordinate(flyover):
    country_codes = []
    for i in range(len(flyover)):
        oneRoute = []
        for j in range(len(flyover[i])):
            oneRoute.append(get_country_coordinate_from_country(flyover[i][j]))
            # print(f"oneRoute[{j}] {oneRoute[j]}")
        country_codes.append(oneRoute)

    return country_codes

def calculate_estimated_time(distance):
    

    # Calculate estimated time based on average flight speed (Assuming 800 km/h)
    # add buffer_time of 1.5 hours
    buffer_time = 1.5
    average_speed_kmh = 800
    estimated_time_hours = distance / average_speed_kmh
    estimated_time_minutes = (estimated_time_hours % 1) * 60
    # Add buffer time
    estimated_time_hours += buffer_time

    return int(estimated_time_hours), int(estimated_time_minutes)






# Function to calculate weighted score
def calculate_weighted_score(passengers, ticket_price, discount):
    # Check if the result is already cached
    if (passengers, ticket_price, discount) in cached_scores:
        return cached_scores[(passengers, ticket_price, discount)]
    
    # Calculate the weighted score
    weighted_score = (weight_discount * discount) + (weight_passengers * passengers)
    
    # Cache the result
    cached_scores[(passengers, ticket_price, discount)] = weighted_score
    
    return weighted_score

def display_top_usable_vouchers(passengers, ticket_price, top_n=5):
    ranked_vouchers = []
    selected_vouchers = set()  
    for _, (p, tp, d) in enumerate(voucher_data):
        if p <= passengers and tp <= ticket_price:
            weighted_score = calculate_weighted_score(p, tp, d)
            heapq.heappush(ranked_vouchers, (-weighted_score, p, tp, d))
            ranked_vouchers.append((-weighted_score, p, tp, d))

    ranked_vouchers.sort()

    top_vouchers = []
    for _, (weighted_score, p, tp, d) in enumerate(ranked_vouchers):
        if len(top_vouchers) >= top_n:
            break  # Stop once we have found the desired number of top vouchers

        # Check if the voucher is already selected
        if (p, tp, d) not in selected_vouchers:
            savings = d / 100 * tp
            top_vouchers.append((p, tp, d, -weighted_score, savings))
            selected_vouchers.add((p, tp, d))

    return top_vouchers

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
   
    distance = round(distance, 2)
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

def ascendingInsertionSort(arr,index):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key[index] < arr[j][index]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def descendingInsertionSort(arr,index):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key[index] > arr[j][index]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def ascendingQuickSort(arr,index):
    if len(arr) <= 10:
        return ascendingInsertionSort(arr,index)
    # pivot set to median distance
    pivot = arr[len(arr) // 2][index]
    # left contains all elements with distance less than pivot
    left = [x for x in arr if x[index] < pivot]
    middle = [x for x in arr if x[index] == pivot]
    # right contains all elements with distance greater than pivot
    right = [x for x in arr if x[index] > pivot]
    # recursively sort left and right
    return ascendingQuickSort(left,index) + middle + ascendingQuickSort(right,index)

def descendingQuickSort(arr,index):
    if len(arr) <= 10:
        return descendingInsertionSort(arr,index)
    # pivot set to median distance
    pivot = arr[len(arr) // 2][index]
    # left contains all elements with distance less than pivot
    left = [x for x in arr if x[index] < pivot]
    middle = [x for x in arr if x[index] == pivot]
    # right contains all elements with distance greater than pivot
    right = [x for x in arr if x[index] > pivot]
    # recursively sort left and right
    return descendingQuickSort(right,index) + middle + descendingQuickSort(left,index)



def sort_by_distance(data, order):
    if order == 'ascending':
        return ascendingQuickSort(data,1)
    elif order == 'descending':
        print("DESCENDING")
        return descendingQuickSort(data,1)
    elif order == 'ascendingPrice':
        print("ascendingPrice")
        return ascendingQuickSort(data,3)
    elif order == 'descendingPrice':
        print("descendingPrice")
        return descendingQuickSort(data,3)
    #price is ,3
    else:
        raise ValueError("Invalid order. Please enter 'ascending' or 'descending'.")


# Function to print flight routes with their total distances
def print_flight_routes(graph, direct_route, routes, response_data, airports, origin, destination,sort_order):
    printed_routes = set()
    direct_data = []
    indirect_data = []
    if direct_route:
        direct_route.sort(key=lambda route: get_flight_prices(route[0], route[1], response_data))
        direct_data = print_route_info(direct_route, response_data, graph, printed_routes)
        direct_data = sort_by_distance(direct_data, sort_order)
    elif routes:
         routes.sort(key=lambda route: min(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1)))
         for i, route in enumerate(routes[:10], start=1):
            if len(route) == 2:
                continue
            else:
                indirect_flight_info = print_route_info(route, response_data, graph, printed_routes)
              
                if indirect_flight_info:
                    indirect_data.extend(indirect_flight_info)
         indirect_data = sort_by_distance(indirect_data, sort_order)
         print(indirect_data)
        
                   

        
        
        
                   

   
    return direct_data, indirect_data

def get_airline_and_cost_for_route(origin, destination, response_data):
    for itinerary in response_data:
        segments = itinerary['itineraries'][0]['segments']
        for segment in segments:
            if segment['departure']['iataCode'] == origin and segment['arrival']['iataCode'] == destination:
                return segment['carrierCode'], float(itinerary['price']['total'])
    return "Unknown", 0.0

# return the output instead of printing it

def find_optimal_route(graph, direct_route, routes, response_data, airports, origin, destination):
    optimal_route = None
    optimal_cost = float('inf')

    if direct_route:
        # Calculate total cost for the direct route
        direct_cost = get_flight_prices(direct_route[0], direct_route[1], response_data)
        if direct_cost < optimal_cost:
            optimal_route = direct_route
            optimal_cost = direct_cost
    elif routes:
        for route in routes:
            total_cost = sum(get_flight_prices(route[j], route[j+1], response_data) for j in range(len(route) - 1))
            if total_cost < optimal_cost:
                optimal_route = route
                optimal_cost = total_cost

    return optimal_route


def print_optimal_route(optimal_route, response_data, graph, airports):
    optimal_route_data = []
    if optimal_route:
        total_distance = 0
       
        for i in range(len(optimal_route) - 1):
            origin, destination = optimal_route[i], optimal_route[i+1]
            distance = dijkstra(graph, origin, destination)
            total_distance += distance
            airline, cost = get_airline_and_cost_for_route(origin, destination, response_data)
           
            optimal_route_data.append((optimal_route, airline, total_distance, cost))
    else:
        optimal_route_data.append(("No optimal route available.", None, None, None, None, None, None))
    
    return optimal_route_data


# Function to handle each flight information
def print_route_info(route_data, response_data, graph, printed_routes):
    total_distance = sum(dijkstra(graph, route_data[j], route_data[j+1]) for j in range(len(route_data) - 1))
    est_time = []
    # calculate time (in Minus &Hours)
    estimated_time_hours, estimated_time_minutes = calculate_estimated_time(
        total_distance
    )
    est_time.append(int(estimated_time_hours))
    est_time.append(int(estimated_time_minutes))

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
                        direct_flights_data.append(([origin, destination], round(total_distance, 2), segment[2], segment[3],est_time,))
            return direct_flights_data
        elif len(route_data) > 2:
            for i in range(len(route_data) - 1):
                origin, destination = route_data[i], route_data[i+1]
                for segment in sorted_segments:
                    if segment[0] == origin and segment[1] == destination:
                        indirect_flights_data.append((route_data, round(total_distance, 2), segment[2], segment[3],est_time,))
                        return  indirect_flights_data



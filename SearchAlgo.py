import pandas as pd
from geopy.distance import geodesic
import time

start = time.time()

# Reading data from the file
# Reading data from the file
routes_with_distance_cols = ['Source airport', 'Destination airport', 'Distance']

routes_with_distance = pd.read_csv('CSC1108/Project/routes_with_distance.csv', usecols=routes_with_distance_cols)

# source_airports = airports[['IATA', 'Latitude', 'Longitude']].rename(columns={'IATA': 'Source airport'})
# destination_airports = airports[['IATA', 'Latitude', 'Longitude']].rename(columns={'IATA': 'Destination airport'})

# routes_with_source = pd.merge(routes_edited, source_airports, on='Source airport', how='left')
# routes_with_destination = pd.merge(routes_with_source, destination_airports, on='Destination airport', how='left')

# Remove entries with null values for coordinates
# routes_with_destination = routes_with_destination.dropna(subset=['Latitude_x', 'Longitude_x', 'Latitude_y', 'Longitude_y'])

# #This part is to check if there are still null values in the dataset not needed in the actual code
# null_inf_index = routes_with_destination[['Latitude_x', 'Longitude_x', 'Latitude_y', 'Longitude_y']].isnull().values.any() 

# Calculate the distance between the source and destination airports in km
# def calculate_distance(row):
#     source = (row['Latitude_x'], row['Longitude_x'])
#     dest = (row['Latitude_y'], row['Longitude_y'])
#     return geodesic(source, dest).kilometers

# Apply the function to the routes_with_coordinates dataset
# This part takes quite awhile to run
# routes_with_destination['Distance'] = routes_with_destination.apply(calculate_distance, axis=1)
# print(routes_with_destination[['Source airport', 'Destination airport', 'Distance']])
#routes_with_destination[['Source airport', 'Latitude_x', 'Longitude_x', 'Destination airport', 'Latitude_y', 'Longitude_y', 'Distance']].to_csv('routes_with_distance.csv', index=False)

class HashTable:
    def __init__(self):
        self.size = 68000
        self.R = 67999  # Choose a prime number smaller than self.size
        self.keys = [None] * self.size
        self.values = [[] for _ in range(self.size)]
        self.routes_with_distance = pd.read_csv('CSC1108/Project/routes_with_distance.csv')

    def hashfunction(self, key):
        return sum(ord(c) for c in key) % self.size
    
    def second_hash(self, key):
        # Second hash function
        return self.R - (sum(ord(c) for c in key) % self.R)

    def rehash(self, key, i):
        #return (oldhash + i**2) % self.size
        
        # Double hashing to resolve collisions
        hashvalue = self.hashfunction(key)
        return (hashvalue + i * self.second_hash(key)) % self.size

    def put(self, key, data):
        hashvalue = self.hashfunction(key)

        if self.keys[hashvalue] is None:
            self.keys[hashvalue] = key
            self.values[hashvalue].append(data)
        else:
            if self.keys[hashvalue] == key:
                self.values[hashvalue].append(data)
            else:
                i = 0
                nextslot = self.rehash(key, i)
                while self.keys[nextslot] is not None and self.keys[nextslot] != key:
                    i += 1
                    nextslot = self.rehash(key, i)

                if self.keys[nextslot] is None:
                    self.keys[nextslot] = key
                self.values[nextslot].append(data)

    # def get(self, key):
    #     startslot = self.hashfunction(key)

    #     data = None
    #     stop = False
    #     found = False
    #     position = startslot
    #     i = 0
    #     while self.keys[position] is not None and not found and not stop:
    #         if self.keys[position] == key:
    #             found = True
    #             data = self.values[position]
    #         else:
    #             i += 1
    #             position = self.rehash(startslot, i)
    #             if position == startslot:
    #                 stop = True
        # return data
        
    def get_route(self, src_airport):
        route = self.routes_with_distance[self.routes_with_distance['Source airport'] == src_airport]
        if not route.empty:
            dest_airports = route['Destination airport'].values
            distances = route['Distance'].values
            return list(zip(dest_airports, distances))
        else:
            return None
        
def partition(arr, low, high):
    i = (low-1)  # index of smaller element
    pivot = arr[high][1]  # pivot

    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if arr[j][1] <= pivot:
            # increment index of smaller element
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i+1)

def quick_sort(arr, low, high, reverse=False):
    if len(arr) == 1:
        return arr
    if low < high:
        # pi is partitioning index, arr[p] is now at right place
        pi = partition(arr, low, high)

        # Separately sort elements before partition and after partition
        quick_sort(arr, low, pi-1, reverse)
        quick_sort(arr, pi+1, high, reverse)

    if reverse:
        arr.reverse()

# Create a new hash table
hash_table = HashTable()

# Iterate over the DataFrame
for row in routes_with_distance.itertuples():
    key = row[1]  # source airport code as the key
    dest_airport = row[2]  # destination airport code
    distance = row[3]  # distance
    value = (dest_airport, distance)  # value is a tuple containing the destination airport and the distance
    hash_table.put(key, value)

end = time.time()
print((end-start), "s")

# Test the hash table
testcase = input("Airport:")  # Take in input the airport code
routes = hash_table.get_route(testcase)
if routes:
    for dest_airport, distance in routes:
        print(f"Destination: {dest_airport}, Distance: {distance}")  # This should print the destination airport and its distance
        
    sort = input("Do you want to sort the routes? (yes/no): ")
    if sort.lower() == "yes":
        order = input("In which order do you want to sort the routes? (ascending/descending): ")
        quick_sort(routes, 0, len(routes)-1, order.lower() == "descending")
        for dest_airport, distance in routes:
            print(f"Destination: {dest_airport}, Distance: {distance}")  # This should print the destination airport and its distance
    if sort.lower() == "no":
        print("No sorting done.")
else:
    print("No routes found from this airport.")
import pandas as pd
from geopy.distance import geodesic
import time
import os

start = time.time()
project_dir = os.getcwd()

# Reading data from the file
# Reading data from the file
routes_with_distance_cols = ['Source airport', 'Destination airport', 'Distance']
csv_file_path = os.path.join(project_dir,  'routes_with_distance.csv')



class HashTable:
    def __init__(self):
        self.size = 68000
        self.R = 67999  # Choose a prime number smaller than self.size
        self.keys = [None] * self.size
        self.values = [[] for _ in range(self.size)]
        self.routes_with_distance = pd.read_csv(csv_file_path, usecols=routes_with_distance_cols)

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
# Iterate over the DataFrame
for row in hash_table.routes_with_distance.itertuples():
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
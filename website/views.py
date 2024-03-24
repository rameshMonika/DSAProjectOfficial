from flask import Blueprint,render_template,request, jsonify
from flask_login import login_required,current_user
from .controllers import read_airports_from_csv,amadeus,construct_graph,print_flight_routes,dfs
import os

views=Blueprint('views',__name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html",user=current_user)


@views.route('/get_route', methods=['POST'])
def search_flights():
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')
    departure_date = data.get('departure_date')
    direct_flight = data.get('direct_flight')

    # Read airports data from CSV file
    current_dir = os.path.dirname(__file__)

    filename = os.path.join(current_dir, 'data', 'airports_Asia.csv')  
    airports = read_airports_from_csv(filename)

    # Construct the graph based on airport distances
    graph = construct_graph(airports)

    # Retrieve flight data for the given origin-destination pair
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=origin,
        destinationLocationCode=destination,
        departureDate=departure_date,
        adults=1,
        currencyCode='SGD',
        nonStop='false',
        max=50
    )

    response_data = response.data

    if response_data:
        direct_route = [origin, destination] if destination in graph.get(origin, []) else None

        if direct_flight:
            direct_data, _ = print_flight_routes(graph, direct_route, [], response_data, airports, origin, destination)
           # _, indirect_data=()
            return jsonify({'direct_flight_data': direct_data})

        else:
            routes = dfs(graph, origin, destination, 2, [origin], response_data)
            
            _, indirect_data = print_flight_routes(graph, [], routes, response_data, airports, origin, destination)
           # direct_data, _=()
            return jsonify({'indirect_flight_data': indirect_data})

    else:
        return jsonify({'error': 'No flight data available.'})


from flask import Flask, request, render_template, jsonify
import pandas as pd
from geopy.distance import geodesic
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)

# Read data
airports_cols = ['Airport ID', 'City', 'Country', 'IATA', 'ICAO', 'Latitude',
                 'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone', 'Type', 'Source']
routes_cols = ['Airline', 'Airline ID', 'Source airport', 'Source airport ID',
               'Destination airport', 'Destination airport ID', 'Codeshare', 'Stops', 'Equipment']
airports = pd.read_csv('data/airports.csv', names=airports_cols,
                       header=None, index_col=None, na_values='\\N')
routes = pd.read_csv('data/routes.csv', names=routes_cols,
                     header=None, index_col=None, na_values='\\N')
source_airports = airports[['IATA', 'Latitude', 'Longitude']].rename(
    columns={'IATA': 'Source airport'})
destination_airports = airports[['IATA', 'Latitude', 'Longitude']].rename(
    columns={'IATA': 'Destination airport'})

routes_with_source = pd.merge(
    routes, source_airports, on='Source airport', how='left')
routes_with_coordinates = pd.merge(
    routes_with_source, destination_airports, on='Destination airport', how='left')

# Remove entries with null values for coordinates
routes_with_coordinates = routes_with_coordinates.dropna(
    subset=['Latitude_x', 'Longitude_x', 'Latitude_y', 'Longitude_y'])

# Calculate distance


def calculate_distance(row):
    source = (row['Latitude_x'], row['Longitude_x'])
    dest = (row['Latitude_y'], row['Longitude_y'])
    return geodesic(source, dest).kilometers


routes_with_coordinates['Distance'] = routes_with_coordinates.apply(
    calculate_distance, axis=1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_route', methods=['GET'])
def get_route():
    source = request.args.get('source')
    destination = request.args.get('destination')
    print(f"Requested route from {source} to {destination}")
    result = routes_with_coordinates[(routes_with_coordinates['Source airport'] == source) & (
        routes_with_coordinates['Destination airport'] == destination)]
    # Replace NaN values with None before converting to JSON
    result_json = result.where(pd.notnull(
        result), None).to_dict(orient='records')
    print("Route details:", result_json)
    return jsonify(result_json)


@app.route('/generate_map')
def generate_map():
    # Define the data for the map
    data = {
        'Airport': ['AER', 'KZN'],
        'Latitude': [43.449902, 55.606201],
        'Longitude': [39.956600, 49.27]
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Plot the route on Mapbox
    fig = px.line_mapbox(df, lat='Latitude', lon='Longitude',
                         hover_name='Airport', title='Route from Source to Destination')

    # Add markers for start and end locations
    fig.add_trace(px.scatter_mapbox(df.head(1), lat='Latitude',
                  lon='Longitude', hover_name='Airport', text='Airport').data[0])
    fig.add_trace(px.scatter_mapbox(df.tail(1), lat='Latitude',
                  lon='Longitude', hover_name='Airport', text='Airport').data[0])

    # Add an arrow from source to destination
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[df['Longitude'][0], df['Longitude'][1]],
        lat=[df['Latitude'][0], df['Latitude'][1]],
        line=dict(width=2, color='blue'),
        showlegend=False,
        hoverinfo='none',
        marker=dict(size=0),
    ))

    # Customize mapbox settings
    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=3,
                      mapbox_center={"lat": 49.5, "lon": 45})

    # Convert the figure to HTML
    map_html = fig.to_html()

    # Write the HTML content to the file
    with open("templates/oneMap.html", "w") as file:
        file.write("<!DOCTYPE html>\n")
        file.write("<html lang=\"en\">\n")
        file.write("<head>\n")
        file.write("<meta charset=\"UTF-8\">\n")
        file.write(
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
        file.write("<title>Map</title>\n")
        file.write(
            "<!-- Add necessary Plotly CDN links here if not already included in the HTML -->\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<div>\n")
        file.write("<!-- Embedded map will be rendered here -->\n")
        file.write(map_html)
        file.write("</div>\n")
        file.write("</body>\n")
        file.write("</html>")

    return "Map generated successfully!"

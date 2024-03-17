import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Define the data
data = {
    'Airport': ['AER', 'KZN'],
    'Latitude': [43.449902, 55.606201],
    'Longitude': [39.956600, 49.27]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Plot the route on Mapbox
fig = px.line_mapbox(df, lat='Latitude', lon='Longitude', hover_name='Airport', title='Route from Source to Destination')

# Add markers for start and end locations
fig.add_trace(px.scatter_mapbox(df.head(1), lat='Latitude', lon='Longitude', hover_name='Airport', text='Airport').data[0])
fig.add_trace(px.scatter_mapbox(df.tail(1), lat='Latitude', lon='Longitude', hover_name='Airport', text='Airport').data[0])


# Add an arrow from source to destination
fig.add_trace(go.Scattermapbox(
    mode = "lines",
    lon = [df['Longitude'][0], df['Longitude'][1]],
    lat = [df['Latitude'][0], df['Latitude'][1]],
    line=dict(width=2, color='blue'),
    showlegend=False,
    hoverinfo='none',
    marker=dict(size=0),
    ))


# Customize mapbox settings
fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=3, mapbox_center = {"lat": 49.5, "lon": 45})

# Show the figure
fig.show()

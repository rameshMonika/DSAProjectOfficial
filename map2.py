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

# Plot the route using Plotly Express
fig = px.line_geo(df, lat='Latitude', lon='Longitude', hover_name='Airport', title='Route from Source to Destination')

# Add markers for start and end locations
fig.add_trace(px.scatter_geo(df.head(1), lat='Latitude', lon='Longitude', hover_name='Airport', text='Airport').data[0])
fig.add_trace(px.scatter_geo(df.tail(1), lat='Latitude', lon='Longitude', hover_name='Airport', text='Airport').data[0])

# Add an arrow from source to destination
fig.add_trace(go.Scattergeo(
    mode = "lines",
    lon = [df['Longitude'][0], df['Longitude'][1]],
    lat = [df['Latitude'][0], df['Latitude'][1]],
    line=dict(width=2, color='blue'),
    showlegend=False,
    hoverinfo='none',
    marker=dict(size=0),
    ))

# Convert the Plotly Express figure to a go.Figure object for further customization
fig = go.Figure(fig)

center_lat = (df['Latitude'].max() + df['Latitude'].min()) / 2
center_lon = (df['Longitude'].max() + df['Longitude'].min()) / 2
zoom = 8  # Adjust the zoom level as needed



# Customize the map projection type and layout
fig.update_geos(projection_type="natural earth")
fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})

# Show the figure
fig.show()

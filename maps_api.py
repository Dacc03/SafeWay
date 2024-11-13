import folium
import googlemaps
from geopy.distance import geodesic
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Set up Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def get_route(origin, destination):
    # Get directions from Google Maps
    directions = gmaps.directions(origin, destination, mode="driving")
    route = directions[0]['legs'][0]['steps']
    
    # Extract latitude and longitude points from the route
    route_coords = [(step['end_location']['lat'], step['end_location']['lng']) for step in route]
    return route_coords

def visualize_route(route_coords, avoid_points, avoid_radius):
    # Initialize the map centered around the start point of the route
    start_point = route_coords[0]
    m = folium.Map(location=start_point, zoom_start=13)

    # Add the route to the map as a blue polyline
    folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(m)

    # Add circles for each avoidance zone (crime location) on the map
    for point in avoid_points:
        folium.Circle(
            location=(point['lat'], point['lng']),
            radius=avoid_radius,
            color="red",
            fill=True,
            fill_opacity=0.3
        ).add_to(m)

    # Add markers for the start and end points
    folium.Marker(route_coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(route_coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(m)

    return m

# Example usage
#origin = "Sta. Teresa 233, Lima, Peru"
#destination = "Av Alameda San Marcos 11, Chorrillos 15067"
#avoid_points = [{"lat": 12.345, "lng": 67.890}, {"lat": 12.346, "lng": 67.891}]  # Crime locations
#avoid_radius = 100  # Radius in meters to avoid

# Get the route and visualize it
#route_coords = get_route(origin, destination)
#map_visual = visualize_route(route_coords, avoid_points, avoid_radius)

# Display the map
#map_visual.save("route_map.html")


import osmnx as ox
import networkx as nx
import folium

# Step 1: Load the city graph
place = "Lima, Peru"
graph = ox.graph_from_place(place, network_type="drive")

# Step 2: Calculate shortest path with modified weights
start_lat = -12.049981
start_lon =-77.007117

end_lat = -12.094566
end_lon = -77.070903
start_coords = (start_lat, start_lon)
end_coords = (end_lat, end_lon)
start_node = ox.distance.nearest_nodes(graph, X=start_coords[1], Y=start_coords[0])
end_node = ox.distance.nearest_nodes(graph, X=end_coords[1], Y=end_coords[0])
shortest_path = nx.shortest_path(graph, start_node, end_node, weight='weight')

# Step 3: Convert nodes in path to coordinates
route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]

# Step 4: Create a folium map centered on the starting point
map_center = [start_coords[0], start_coords[1]]
route_map = folium.Map(location=map_center, zoom_start=14)

# Step 5: Add the route as a line on the map
folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)

# Step 6: Add markers for start and end points
folium.Marker(location=start_coords, popup="Start", icon=folium.Icon(color="green")).add_to(route_map)
folium.Marker(location=end_coords, popup="End", icon=folium.Icon(color="red")).add_to(route_map)

# Step 7: Optionally, add circles for crime locations to visualize risky areas
crime_points = [(crime_lat, crime_lon) for crime_lat, crime_lon in get_crime_data()]
for crime_location in crime_points:
    folium.Circle(
        location=crime_location,
        radius=200,  # Adjust radius based on your application's needs
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.3
    ).add_to(route_map)

# Step 8: Display the map
route_map.save("route_map.html")

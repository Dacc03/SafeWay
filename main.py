import tkinter as tk
import customtkinter as ctk
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
import networkx as nx
import osmnx as ox
import webbrowser
import os
import requests
import logging

#datos de prueba
crime_points = [
    (-12.10434022487609, -77.03088303440502, 3),
]

# Debugging purposes.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_coordinates(location):
    geolocator = Nominatim(user_agent="safeway_app")
    location = geolocator.geocode(location)
    if location:
        return location.latitude, location.longitude
    else:
        return None


def calculate_route(start, end):
    try:
        logging.debug(f"Calculando ruta desde {start} hasta {end}")

        center_lat = (start[0] + end[0]) / 2
        center_lon = (start[1] + end[1]) / 2
        dist = max(geodesic(start, end).km, 5) * 1000  # convertir a metros

        logging.debug(
            f"Obteniendo grafo para el área centrada en ({center_lat}, {center_lon}) con distancia {dist} metros")
        G = ox.graph_from_point((center_lat, center_lon), dist=dist, network_type="drive")

        start_node = ox.nearest_nodes(G, start[1], start[0])
        end_node = ox.nearest_nodes(G, end[1], end[0])

        route = nx.shortest_path(G, start_node, end_node, weight='length')

        logging.debug("Ruta calculada exitosamente")
        return G, route
    except Exception as e:
        logging.error(f"Error al calcular la ruta: {str(e)}", exc_info=True)
        raise


def calculate_multiple_routes(start, end, amount):
    try:
        logging.debug(f"Calculando ruta desde {start} hasta {end}")

        center_lat = (start[0] + end[0]) / 2
        center_lon = (start[1] + end[1]) / 2
        dist = max(geodesic(start, end).km, 5) * 1000  # convertir a metros

        logging.debug(
            f"Obteniendo grafo para el área centrada en ({center_lat}, {center_lon}) con distancia {dist} metros")
        G = ox.graph_from_point((center_lat, center_lon), dist=dist, network_type="drive")

        start_node = ox.nearest_nodes(G, start[1], start[0])
        end_node = ox.nearest_nodes(G, end[1], end[0])

        routes = ox.k_shortest_paths(G, start_node, end_node, amount)

        logging.debug("Ruta calculada exitosamente")
        return G, routes
    except Exception as e:
        logging.error(f"Error al calcular la ruta: {str(e)}", exc_info=True)
        raise


def create_map(start, end, G, route):
    map = folium.Map(location=start, zoom_start=13)
    folium.Marker(start, popup="Inicio", icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(end, popup="Destino", icon=folium.Icon(color='red')).add_to(map)
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
    folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.8).add_to(map)
    return map


def create_map_with_multiple_routes(start, end, G, routes):
    map = folium.Map(location=start, zoom_start=13)

    folium.Marker(start, popup="Inicio", icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(end, popup="Destino", icon=folium.Icon(color='red')).add_to(map)

    colors = ['blue', 'purple', 'red', 'green', 'black']  # Can cycle through colors
    for idx, route in enumerate(routes):
        # Extract the coordinates for the current route
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

        # Add a PolyLine for the current route, with different colors for each route
        folium.PolyLine(route_coords, color=colors[idx % len(colors)], weight=4, opacity=0.8).add_to(map)

    return map


class SafewayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.info_text = None
        self.progress = None
        self.end_entry = None
        self.start_entry = None

        self.title("SAFEWAY")
        self.geometry("800x600")
        self.configure(fg_color="#2c3e50")
        self.create_widgets()

    def create_widgets(self):
        # Window
        main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#34495e")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(main_frame, text="SAFEWAY", font=("Roboto", 36, "bold"), text_color="#ecf0f1")
        title_label.pack(pady=20)

        # Input
        input_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#2c3e50")
        input_frame.pack(padx=20, pady=10, fill="x")

        # Location
        start_label = ctk.CTkLabel(input_frame, text="Ubicación de inicio:", font=("Roboto", 14), text_color="#bdc3c7")
        start_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.start_entry = ctk.CTkEntry(input_frame, width=300, font=("Roboto", 14))
        self.start_entry.grid(row=0, column=1, padx=10, pady=10)

        # My current location button
        current_location_button = ctk.CTkButton(
            input_frame, text="Obtener ubicación actual",
            command=self.get_current_location,
            font=("Roboto", 14), fg_color="#3498db", hover_color="#2980b9"
        )
        current_location_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Destiny
        end_label = ctk.CTkLabel(input_frame, text="Destino:", font=("Roboto", 14), text_color="#bdc3c7")
        end_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.end_entry = ctk.CTkEntry(input_frame, width=300, font=("Roboto", 14))
        self.end_entry.grid(row=2, column=1, padx=10, pady=10)

        # Calculate routes
        calculate_button = ctk.CTkButton(
            main_frame, text="Calcular Ruta",
            command=self.calculate_and_show_multiple_routes,  # command=self.calculate_and_show_route
            font=("Roboto", 16, "bold"), fg_color="#2ecc71", hover_color="#27ae60"
        )
        calculate_button.pack(pady=20)

        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame, width=400)
        self.progress.pack(pady=10)
        self.progress.set(0)

        # Output console
        self.info_text = ctk.CTkTextbox(main_frame, height=100, font=("Roboto", 14), text_color="#ecf0f1")
        self.info_text.pack(padx=20, pady=10, fill="x")
        self.info_text.insert(
            "1.0",
            "Bienvenido a SAFEWAY. Ingresa tu ubicación de inicio y destino para calcular la ruta más segura."
        )

    def get_current_location(self):
        try:
            response = requests.get('https://ipapi.co/json/')
            data = response.json()
            if 'city' in data and 'country_name' in data:
                location = f"{data['city']}, {data['country_name']}"
                self.start_entry.delete(0, tk.END)
                self.start_entry.insert(0, location)
                self.update_info(f"Ubicación detectada: {location}")
            else:
                self.update_info("No se pudo obtener la ubicación actual.")
        except Exception as e:
            self.update_info(f"Error al obtener la ubicación: {str(e)}")

    def calculate_and_show_route(self):
        self.progress.start()
        start_location = self.start_entry.get()
        end_location = self.end_entry.get()

        logging.debug(f"Inicio: {start_location}, Destino: {end_location}")

        start_coords = get_coordinates(start_location)
        end_coords = get_coordinates(end_location)

        logging.debug(f"Coordenadas de inicio: {start_coords}, Coordenadas de destino: {end_coords}")

        if not start_coords or not end_coords:
            self.update_info("No se pudo encontrar una o ambas ubicaciones.")
            self.progress.stop()
            return

        try:
            G, route = calculate_route(start_coords, end_coords)
            map = create_map(start_coords, end_coords, G, route)
            map_file = "safeway_route.html"
            map.save(map_file)
            webbrowser.open('file://' + os.path.realpath(map_file))
            self.update_info("Ruta calculada y mapa generado. Abriendo en su navegador...")
        except Exception as e:
            logging.error(f"Error en calculate_and_show_route: {str(e)}", exc_info=True)
            self.update_info(f"Ocurrió un error al calcular la ruta: {str(e)}")

        self.progress.stop()

    def calculate_and_show_multiple_routes(self):
        self.progress.start()
        start_location = self.start_entry.get()
        end_location = self.end_entry.get()

        logging.debug(f"Inicio: {start_location}, Destino: {end_location}")

        start_coords = get_coordinates(start_location)
        end_coords = get_coordinates(end_location)

        logging.debug(f"Coordenadas de inicio: {start_coords}, Coordenadas de destino: {end_coords}")

        if not start_coords or not end_coords:
            self.update_info("No se pudo encontrar una o ambas ubicaciones.")
            self.progress.stop()
            return

        try:
            G, routes = calculate_multiple_routes(start_coords, end_coords, 3)

            map = create_map_with_multiple_routes(start_coords, end_coords, G, routes)
            map_file = "safeway_route.html"
            map.save(map_file)
            webbrowser.open('file://' + os.path.realpath(map_file))
            self.update_info("Ruta calculada y mapa generado. Abriendo en su navegador...")
        except Exception as e:
            logging.error(f"Error en calculate_and_show_route: {str(e)}", exc_info=True)
            self.update_info(f"Ocurrió un error al calcular la ruta: {str(e)}")

        self.progress.stop()

    def update_info(self, message):
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", message)


if __name__ == "__main__":
    app = SafewayApp()
    app.mainloop()

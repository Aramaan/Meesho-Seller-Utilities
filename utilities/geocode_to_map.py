import folium

locations = [
    {"name": "Cuttack", "lat": 20.4625, "lon": 85.8830},
    {"name": "Khurda", "lat": 20.1820, "lon": 85.6160},
]

map_view = folium.Map(location=[20.5, 85.8], zoom_start=8)

for location in locations:
    folium.Marker(
        [location["lat"], location["lon"]],
        popup=location["name"]
    ).add_to(map_view)

map_view.fit_bounds([
    [location["lat"], location["lon"]]
    for location in locations
])

map_view.save("map.html")
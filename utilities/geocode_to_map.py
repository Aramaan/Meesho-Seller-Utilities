import folium
import polars as pl

locations = pl.DataFrame(
    {
        "name": ["Cuttack", "Khurda"],
        "lat": [20.4625, 20.1820],
        "lon": [85.8830, 85.6160],
    }
)


def create_map(locations: pl.DataFrame):
    map_view = folium.Map(location=[20.5, 85.8], zoom_start=8)

    for location in locations.iter_rows(named=True):
        folium.Marker(
            [location["lat"], location["lon"]],
            popup=location["name"]
        ).add_to(map_view)

    map_view.fit_bounds([
        [row["lat"], row["lon"]]
        for row in locations.select(["lat", "lon"]).iter_rows(named=True)
    ])

    map_view.save("map.html")


create_map(locations)
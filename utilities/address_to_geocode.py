"Creating a script that that takes an address as input and returns the latitude and longitude coordinates using the Google Maps Geocoding API."

import googlemaps #geopy, geocoder

client = googlemaps.Client(key="YOUR_GOOGLE_API_KEY")

result = client.geocode("Cuttack, Odisha, India")

if result:
    location = result[0]["geometry"]["location"]
    print("Latitude:", location["lat"])
    print("Longitude:", location["lng"])

"Create a function to calculate the distance between two latitude and longitude"
" coordinates using the Haversine formula."

def distance_km(lat1, lon1, lat2, lon2):
	"""Return the great-circle distance between two coordinates in kilometres."""
	earth_radius_km = 6371.0
	d_lat = radians(lat2 - lat1)
	d_lon = radians(lon2 - lon1)
	lat1, lat2 = radians(lat1), radians(lat2)

	a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
	return 2 * earth_radius_km * asin(sqrt(a))
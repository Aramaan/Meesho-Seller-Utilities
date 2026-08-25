from math import radians, sin, cos, sqrt, asin
import os
import re
import googlemaps

"""I want to create a function that takes a PINCODE as input and returns the latitude
and longitude coordinates using the Google Maps Geocoding API. I will use the
 `googlemaps` library for this purpose. Here's how I can implement it:"""

import os
import re
import googlemaps


def pincode_to_latlong(pincode):
    """Return (latitude, longitude) for an Indian PIN code."""
    pincode = str(pincode).strip()

    if not re.fullmatch(r"\d{6}", pincode):
        raise ValueError("PIN code must contain exactly 6 digits.")

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise RuntimeError("Set the GOOGLE_MAPS_API_KEY environment variable.")

    client = googlemaps.Client(key=api_key)
    results = client.geocode(f"{pincode}, India")

    if not results:
        return None

    location = results[0]["geometry"]["location"]
    return location["lat"], location["lng"]

"""Create a function to calculate the distance between two latitude and longitude
 coordinates using the Haversine formula."""

def distance_km(lat1, lon1, lat2, lon2):
	"""Return the great-circle distance between two coordinates in kilometres."""
	earth_radius_km = 6371.0
	d_lat = radians(lat2 - lat1)
	d_lon = radians(lon2 - lon1)
	lat1, lat2 = radians(lat1), radians(lat2)

	a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
	return 2 * earth_radius_km * asin(sqrt(a))


if __name__ == "__main__":
	lat1, lon1 = map(float, input("Enter first latitude and longitude: ").split())
	lat2, lon2 = map(float, input("Enter second latitude and longitude: ").split())
	print(f"Distance: {distance_km(lat1, lon1, lat2, lon2):.2f} km")



import json
import math

def haversine(lat1, lon1, lat2, lon2):
    # Hitung jarak menggunakan rumus haversine
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def find_nearest_location(epicenter_lat, epicenter_lon, poi_json_path="C:/Users/LEGION/Documents/earthquake-main/datas/poi_sumbar.json"):
    with open(poi_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    min_distance = float('inf')
    nearest = None

    for poi in data:
        lat = float(poi['Latitude'])
        lon = float(poi['Longitude'])
        distance = haversine(epicenter_lat, epicenter_lon, lat, lon)
        if distance < min_distance:
            min_distance = distance
            nearest = poi

    if nearest:
        # Hitung arah mata angin
        bearing = calculate_bearing(epicenter_lat, epicenter_lon, float(nearest['Latitude']), float(nearest['Longitude']))
        direction = bearing_to_cardinal(bearing)

        location_text = f"{min_distance:.0f} km {direction} {nearest['Kecamatan'].strip()}, {nearest['Kab/Kota'].strip()}"
        return location_text
    else:
        return "Unknown Location"

def calculate_bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    x = math.sin(delta_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - (math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    return (bearing + 360) % 360

def bearing_to_cardinal(bearing):
    directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest', 'North']
    idx = int((bearing + 22.5) // 45)
    return directions[idx]

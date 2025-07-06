from flask import jsonify
import datetime

def get_wavefront(event_lat, event_lon, origin_time_iso, max_time_seconds=60, time_step=5):
    """
    Membuat data propagasi P dan S wave dalam format GeoJSON untuk TimestampedGeoJson.
    """

    p_velocity = 6.0  # km/s
    s_velocity = 3.5  # km/s

    origin_time = datetime.datetime.fromisoformat(origin_time_iso)
    features = []

    for t in range(0, max_time_seconds + time_step, time_step):
        timestamp = (origin_time + datetime.timedelta(seconds=t)).isoformat()

        p_radius = p_velocity * t * 1000  # meter
        s_radius = s_velocity * t * 1000  # meter

        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [event_lon, event_lat],
            },
            'properties': {
                'time': timestamp,
                'style': {'color': 'blue'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'blue',
                    'fillOpacity': 0.1,
                    'stroke': True,
                    'radius': p_radius / 1000  # radius dalam km
                }
            }
        })

        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [event_lon, event_lat],
            },
            'properties': {
                'time': timestamp,
                'style': {'color': 'red'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'red',
                    'fillOpacity': 0.1,
                    'stroke': True,
                    'radius': s_radius / 1000
                }
            }
        })

    return jsonify({
        'type': 'FeatureCollection',
        'features': features
    })

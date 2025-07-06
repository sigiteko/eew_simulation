import folium
import folium.plugins

def get_magnitude_map(df, fault_line, stations_df, show_epicenter=False, epicenter_lat=None, epicenter_lon=None, show_radius=False):
    # Inisialisasi peta di tengah-tengah data gempa
    magnitude_map = folium.Map(
        location=[df['latitude'].mean(), df['longitude'].mean()],
        zoom_start=7,
        control_scale=True
    )


    # Tambahkan semua gempa
    for index, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['magnitude'] * 2,
            popup=row.get('address', f"M {row['magnitude']}"),
            color='#3186cc',
            fill=True,
            fill_color='#3186cc'
        ).add_to(magnitude_map)

    # Tambahkan semua stasiun
    for idx, station in stations_df.iterrows():
        folium.CircleMarker(
            location=[station['Latitude'], station['Longitude']],
            radius=5,
            color='black',
            fill=True,
            fill_color='white',
            fill_opacity=1,
            popup=station['nama_stasiun']
        ).add_to(magnitude_map)

    # Tambahkan patahan
    folium.GeoJson(
        fault_line,
        name='Fault Line',
        style_function=lambda feature: {
            'fillColor': '#ff0000',
            'color': '#ff0000',
            'weight': 1,
            'dashArray': '5, 5'
        }
    ).add_to(magnitude_map)

    # Tambahkan epicenter dan radius
    if show_epicenter and epicenter_lat is not None and epicenter_lon is not None:
        folium.Marker(
            location=[epicenter_lat, epicenter_lon],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(magnitude_map)

    # Lapisan tambahan
    folium.TileLayer('OpenStreetMap').add_to(magnitude_map)
    folium.LayerControl().add_to(magnitude_map)
    folium.plugins.Fullscreen(position='topright').add_to(magnitude_map)
    folium.plugins.LocateControl().add_to(magnitude_map)


    return magnitude_map._repr_html_()

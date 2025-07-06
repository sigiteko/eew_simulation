import pandas as pd
from flask import render_template
from app.api.get_earthquake import get_earthquake
from app.api.get_fault_line import get_fault_line
from app.api.get_magnitude_map import get_magnitude_map
from app.api.location_finder import find_nearest_location
from obspy.geodetics import gps2dist_azimuth
from app.api.load_stations import load_station_data
from app.api.get_contour import (
    load_data,
    merge_coordinates,
    save_mmi_overlay_image,
    map_station_indices,
)
from geopy.distance import geodesic


def index_page(last_day):
    # Baca data prediksi Mean_Mag dan event gempa
    mag_df = pd.read_csv("datas/event_eval_summary.csv")
    #event_id = "2024-02-23T074628_5.3"
    event_id = "2022-02-25T013928_6.2"
    #event_id = "2023-04-24T200054_6.9"
    #event_id = "2024-01-08T095132_5.0"
    #event_id = "2024-01-27T165058_4.6" 
    df = get_earthquake(event_id=event_id)

    arrival_df = pd.read_csv("datas/arrivaltime.csv")
    arrival_df = arrival_df.rename(columns={"P-wave Marker Sample": "P_arrival"})

    fault_line = get_fault_line()

    stations_df = load_station_data()
    station_list = arrival_df["Station"].unique()
    stations_df = stations_df[stations_df["nama_stasiun"].isin(station_list)]
    stations = stations_df.to_dict(orient="records")

    df_pga, df_coords = load_data()
    df_pga = df_pga[df_pga["EventID"] == event_id]
    df_coords = df_coords[df_coords["EventID"] == event_id]

    station_coords = pd.read_csv("datas/rekap_stations_coords.csv")
    station_coords = station_coords.rename(columns={"nama_stasiun": "Station"})
    df_coords = df_coords.merge(
        station_coords[["Station", "Kabupaten", "Kecamatan"]],
        on="Station", how="left"
    )

    coords_df, df_ordered = map_station_indices(df_coords)
    df_pga = merge_coordinates(df_pga, coords_df, df_coords)
    mmi_images = save_mmi_overlay_image(df_pga)

    site_lat = -0.95
    site_lon = 100.35

    station_coords = station_coords.rename(columns={"nama_stasiun": "Station"})
    arrival_df = arrival_df.merge(
        station_coords[["Station", "Kabupaten", "Kecamatan"]],
        on="Station", how="left"
    )

    filtered = arrival_df[arrival_df["EventID"] == event_id].copy()
    filtered["P_arrival_time"] = filtered["P_arrival"] / 100.0
    filtered = filtered.sort_values("P_arrival_time")

    pwave_arrival = filtered[[
        "Station", "Latitude", "Longitude", "P_arrival_time", "Kabupaten", "Kecamatan"
    ]].to_dict(orient="records")

    if not df.empty:
        latest_event = df.iloc[0]
        magnitude = latest_event["magnitude"]
        lat = latest_event["latitude"]
        lon = latest_event["longitude"]
        remaining_time = 12
        origin_time = pd.to_datetime(latest_event["date"]).isoformat() + "Z"
        origin_time1 = pd.to_datetime(latest_event["date"]).strftime("%Y-%m-%d %H:%M:%S UTC")
        depth = latest_event["dept"]
        location_description = find_nearest_location(lat, lon)

        # Ambil MMI prediksi dari stasiun PDSI
        pdsi_mmi = df_pga[df_pga["Station"] == "PDSI"]

        if not pdsi_mmi.empty and "MMI_Pred" in pdsi_mmi.columns:
            intensity = pdsi_mmi.sort_values("Time").iloc[-1]["MMI_Pred"]
        else:
            intensity = "-"

        mmi_timeseries = df_pga[["Time", "Station", "Kecamatan", "Kabupaten", "MMI_Pred", "Latitude", "Longitude"]].dropna().copy()
        mmi_timeseries = mmi_timeseries.sort_values("Time")

        # Jika kolom Station belum diisi (misalnya hasil join tidak lengkap), cari stasiun terdekat berdasarkan koordinat
        if mmi_timeseries["Station"].isnull().any():
            def find_nearest_station_name(lat, lon, stations):
                return min(
                    stations,
                    key=lambda s: geodesic((lat, lon), (s["Latitude"], s["Longitude"])).meters
                )["Station"]

            mmi_timeseries["Station"] = mmi_timeseries.apply(
                lambda row: find_nearest_station_name(row["Latitude"], row["Longitude"], stations),
                axis=1
            )

        mmi_series = [
            {
                "time": round(row["Time"], 2),
                "region": f"{row['Kecamatan']} - {row['Kabupaten']}",
                "station": row["Station"],  # ✅ Ini dibutuhkan oleh JS
                "mmi": row["MMI_Pred"],
                "lat": row["Latitude"],
                "lon": row["Longitude"]
            }
            for _, row in mmi_timeseries.iterrows()
        ]

        mmi_true_list = df_pga[["Kecamatan", "Kabupaten", "MMI_True", "Latitude", "Longitude"]].dropna()

        mmi_true_series = [
            {
                "region": f"{row['Kecamatan']} - {row['Kabupaten']}",
                "mmi": row["MMI_True"],
                "lat": row["Latitude"],
                "lon": row["Longitude"]
            }
            for _, row in mmi_true_list.iterrows()
        ]

        mag_data = mag_df[mag_df["EventID"] == event_id].copy()
        mag_data["Time"] = pd.to_timedelta(mag_data["Time"], unit="s")
        mag_data = mag_data.sort_values("Time")

        mean_mag_series = [
            {"time": row["Time"].total_seconds(), "value": row["Mean_Mag"]}
            for _, row in mag_data.iterrows()
        ]

        pred_loc_series = [
            {
                "time": row["Time"].total_seconds(),
                "lat": row["Pred_Lat"],
                "lon": row["Pred_Lon"],
                "depth": row["Pred_Depth"],
                "location_description": find_nearest_location(row["Pred_Lat"], row["Pred_Lon"])
            }
            for _, row in mag_data.iterrows()
        ]

        true_epicenter = {
            "lat": mag_data.iloc[0]["True_Lat"],
            "lon": mag_data.iloc[0]["True_Lon"],
            "mag": mag_data.iloc[0]["True_Mag"]
        }
    else:
        magnitude, intensity, lat, lon = 0, "-", 0, 0
        remaining_time, origin_time, origin_time1, depth = 0, "-", "-", 0
        location_description, true_epicenter = "-", {"lat": 0, "lon": 0, "mag": 0}

    _magnitude_map = get_magnitude_map(
        df=df,
        fault_line=fault_line,
        stations_df=stations_df,
        show_epicenter=True,
        epicenter_lat=lat,
        epicenter_lon=lon,
        show_radius=True
    )

    return render_template(
        "index.html",
        magnitude_map=_magnitude_map,
        magnitude=magnitude,
        intensity=intensity,
        remaining_time=remaining_time,
        origin_time=origin_time,
        origin_time1=origin_time1,
        lat=lat,
        lon=lon,
        depth=depth,
        location_description=location_description,
        epicenter_lat=lat,
        epicenter_lon=lon,
        site_lat=site_lat,
        site_lon=site_lon,
        stations=stations_df.to_dict(orient="records"),
        fault_line=fault_line,
        mean_mag_series=mean_mag_series,
        pred_loc_series=pred_loc_series,
        pwave_arrival=pwave_arrival,
        true_epicenter=true_epicenter,
        mmi_images=mmi_images,
        mmi_series=mmi_series,
        mmi_true_series=mmi_true_series
    )

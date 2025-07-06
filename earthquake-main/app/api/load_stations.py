import pandas as pd

def load_station_data():
    station_data = pd.read_csv("datas/rekap_stations_coords.csv")  # Sesuaikan path
    station_data = station_data.dropna()
    return station_data

import pandas as pd

def get_earthquake(last_day=None, event_id=None):
    """
    Membaca data gempa dari event_metadata.xlsx.
    Bisa ambil semua event, atau event tertentu berdasarkan EventID.
    """

    # Load file Excel
    df = pd.read_excel('datas/event_metadata.xlsx')

    # Mapping kolom
    column_mapping = {
        'Time': 'date',
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Depth/Km': 'dept',
        'Magnitude': 'magnitude',
        'EventLocationName': 'address'
    }
    df = df.rename(columns=column_mapping)

    # Pastikan semua kolom yang dibutuhkan ada
    required_columns = ['magnitude', 'latitude', 'longitude', 'date', 'address', 'dept']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Kolom berikut tidak ditemukan setelah mapping: {missing}")

    # Sort berdasarkan waktu
    df = df.sort_values('date', ascending=False).reset_index(drop=True)

    # Kalau event_id spesifik diberikan
    if event_id is not None:
        if '#EventID' not in df.columns:
            raise ValueError("Kolom '#EventID' tidak ditemukan di file event_metadata.xlsx.")
        
        df = df[df['#EventID'] == event_id]

    # Kalau mau limit jumlah event terakhir
    if last_day is not None:
        df = df.head(last_day)

    return df

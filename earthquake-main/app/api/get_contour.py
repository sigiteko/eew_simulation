import os
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import shapefile  # from pyshp
from shapely.geometry import shape, Point
from matplotlib.path import Path
import numpy as np
import time


def load_data(pga_path="datas/event_eval_pga_all.csv", arrival_path="datas/arrivaltime.csv"):
    df_pga = pd.read_csv(pga_path)
    df_coords = pd.read_csv(arrival_path)
    return df_pga, df_coords


def map_station_indices(df_coords):
    df_coords = df_coords.copy()
    df_coords["P_arrival_time"] = df_coords["P-wave Marker Sample"] / 100.0
    df_single_event = df_coords.drop_duplicates(subset=["Station"])
    df_ordered = df_single_event.sort_values(["P_arrival_time", "Station"]).reset_index(drop=True)

    station_index_map = {
        i: (row.Latitude, row.Longitude)
        for i, row in df_ordered.iterrows()
    }

    coords_df = pd.DataFrame([
        {"Station_Index": i, "Latitude": lat, "Longitude": lon}
        for i, (lat, lon) in station_index_map.items()
    ])

    return coords_df, df_ordered


def kategori_mmi(pga_log10):
    if pga_log10 < np.log10(0.0049):
        return 'I'
    elif pga_log10 < np.log10(0.029):
        return 'II-III'
    elif pga_log10 < np.log10(0.275):
        return 'IV'
    elif pga_log10 < np.log10(0.609):
        return 'V'
    elif pga_log10 < np.log10(1.177):
        return 'VI'
    elif pga_log10 < np.log10(2.157):
        return 'VII'
    elif pga_log10 < np.log10(3.922):
        return 'VIII'
    elif pga_log10 < np.log10(7.355):
        return 'IX'
    else:
        return 'X+'


def merge_coordinates(df_pga, coords_df, df_coords=None):
    merged = df_pga.merge(coords_df, on="Station_Index", how="left")

    if df_coords is not None:
        df_unique = df_coords.drop_duplicates(subset=["Latitude", "Longitude"])
        merged = merged.merge(
            df_unique[["Latitude", "Longitude", "Station", "Kabupaten", "Kecamatan"]],
            on=["Latitude", "Longitude"], how="left"
        )

    if "PGA_Pred" in merged.columns:
        merged["MMI_Pred"] = merged["PGA_Pred"].apply(kategori_mmi)
    if "PGA_True" in merged.columns:
        merged["MMI_True"] = merged["PGA_True"].apply(kategori_mmi)

    columns_order = [
        "Model", "EventID", "Time", "Station_Index", "Station",
        "Latitude", "Longitude", "Kabupaten", "Kecamatan",
        "PGA_Pred", "MMI_Pred", "PGA_True", "MMI_True"
    ]
    final_cols = [col for col in columns_order if col in merged.columns]
    return merged[final_cols]


def create_mmi_image(group, file_path, land_shp="datas/ne_10m_admin_0_countries_idn.shp"):
    x = group['Longitude'].values
    y = group['Latitude'].values
    z = group['MMI'].values.astype(float)

    # Buat grid interpolasi dengan margin
    margin = 0.5
    xi = np.linspace(min(x) - margin, max(x) + margin, 150)
    yi = np.linspace(min(y) - margin, max(y) + margin, 150)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolasi cubic
    from scipy.interpolate import griddata
    zi = griddata((x, y), z, (xi, yi), method='cubic')

    # === MASKING DARATAN DENGAN SHP CEPAT ===
    sf = shapefile.Reader(land_shp)
    land_shapes = [shape(s.__geo_interface__) for s in sf.shapes()]

    points = np.vstack((xi.flatten(), yi.flatten())).T
    mask_flat = np.zeros(points.shape[0], dtype=bool)

    for land in land_shapes:
        if not land.is_valid:
            continue
        if land.geom_type == 'Polygon':
            path = Path(np.array(land.exterior.coords))
            mask_flat |= path.contains_points(points)
        elif land.geom_type == 'MultiPolygon':
            for poly in land.geoms:
                path = Path(np.array(poly.exterior.coords))
                mask_flat |= path.contains_points(points)

    mask = mask_flat.reshape(xi.shape)
    zi_masked = np.ma.masked_where(~mask, zi)

    # === Plotting ===
    mmi_colors = [
        "#d0f0ff", "#a0e0ff", "#60f0c0", "#f0ff60",
        "#fff060", "#ffc040", "#ff8040", "#ff4040", "#c00000"
    ]
    mmi_bounds = [0, 2, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.1]
    cmap = ListedColormap(mmi_colors)
    norm = BoundaryNorm(mmi_bounds, cmap.N)

    plt.figure(figsize=(6, 6), dpi=100)
    plt.axis('off')
    # GUNAKAN extent dari hasil grid xi dan yi → lebih akurat
    plt.imshow(zi_masked, extent=(xi.min(), xi.max(), yi.min(), yi.max()),
               origin='lower', cmap=cmap, norm=norm)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.savefig(file_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

    # Kembalikan bounds yang cocok dengan extent ini
    return [[float(yi.min()), float(xi.min())], [float(yi.max()), float(xi.max())]]



def save_mmi_overlay_image(df, output_folder="app/static/images"):
    os.makedirs(output_folder, exist_ok=True)
    mmi_images = []

    mmi_numeric_map = {
        'I': 1.0, 'II-III': 2.5, 'IV': 4.0, 'V': 5.0,
        'VI': 6.0, 'VII': 7.0, 'VIII': 8.0, 'IX': 9.0, 'X+': 10.0
    }

    df = df.copy()
    df["MMI_Pred"] = df["MMI_Pred"].astype(str)
    df["MMI"] = df["MMI_Pred"].map(mmi_numeric_map)

    grouped = df.groupby("Time")
    for t, group in grouped:
        filename = f"mmi_{t:.1f}.png"
        file_path = os.path.join(output_folder, filename)

        start = time.perf_counter()
        bounds = create_mmi_image(group, file_path)  # ← bounds dikembalikan dari fungsi ini
        end = time.perf_counter()
        duration = end - start

        print(f"[{t:.1f}s] MMI image created in {duration:.3f} seconds")

        mmi_images.append({
            "time": round(float(t), 1),
            "file": f"/static/images/{filename}",
            "bounds": bounds,  # ← EPSG:4326 [ [lat1, lon1], [lat2, lon2] ]
            "duration_sec": round(duration, 3)
        })

    return mmi_images

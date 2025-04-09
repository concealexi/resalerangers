import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta

hdb_data = pd.read_csv("datasets/hdb_informations.csv")
trans_data = pd.read_csv("datasets/hdb_final_dataset.csv")
trans_data['date'] = pd.to_datetime(trans_data['month'])

# Flat type mapping (can be extended)
flat_map = {
    "1 ROOM": "flat_type_1 ROOM",
    "2 ROOM": "flat_type_2 ROOM",
    "3 ROOM": "flat_type_3 ROOM",
    "4 ROOM": "flat_type_4 ROOM",
    "5 ROOM": "flat_type_5 ROOM",
    "EXECUTIVE": "flat_type_EXECUTIVE",
    "MULTI-GENERATION": "flat_type_MULTI-GENERATION"
}

def get_transactions(postal_code, user_flat):
    # Validate postal code, if no match, hit error
    filtered = hdb_data[hdb_data['postal_code'].astype(str) == str(postal_code)]
    if filtered.empty:
        raise ValueError(f"Postal code {postal_code} not found in HDB dataset.") #if you want to hit error
        #return pd.DataFrame(columns=['date', 'address', 'adjusted_resale_price'])  #if you want empty df

    # Validate flat type, if no match, hit error
    flat_key = flat_map.get(user_flat.upper().strip())
    if not flat_key or flat_key not in trans_data.columns:
        raise ValueError(f"Unsupported or missing flat type '{user_flat}'") #if you want to hit error
        #return pd.DataFrame(columns=['date', 'address', 'adjusted_resale_price']) #if you want empty df
    
    coord_row = filtered.iloc[0]
    hdb_coords = (coord_row['latitude'], coord_row['longitude'])
    hdb_point = gpd.GeoSeries([Point(hdb_coords[1], hdb_coords[0])], crs="EPSG:4326").to_crs(epsg=3857)
    # Create GeoDataFrame with distances
    gdf = gpd.GeoDataFrame(
        hdb_data,
        geometry=[Point(xy) for xy in zip(hdb_data['longitude'], hdb_data['latitude'])],
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    gdf['distance'] = gdf.geometry.distance(hdb_point.iloc[0])
    nearest_hdbs = gdf.nsmallest(50, 'distance')
    hdb_1km = gdf[gdf['distance'] <= 1000]
    # Filter transactions
    df_nearby = trans_data[trans_data['postal_code'].astype(str).isin(nearest_hdbs['postal_code'].astype(str))]
    trans_1km = trans_data[trans_data['postal_code'].astype(str).isin(hdb_1km['postal_code'].astype(str))]
    df_same_type = df_nearby[df_nearby[flat_key] == 1]
    same_type_1km = trans_1km[trans_1km[flat_key]==1]
    one_year_ago = datetime(2025, 1, 1) - timedelta(days=2*365)
    l_4months = datetime(2025, 1, 1) - timedelta(days=120)
    df_recent = df_same_type[df_same_type['date'] >= one_year_ago]

    recent_1km = same_type_1km[same_type_1km['date'] >= l_4months]
 

    df_recent_sorted = df_recent.sort_values(by='date', ascending=False)
    df_deduped = df_recent_sorted.drop_duplicates(subset='address', keep='first')
    df_with_dist = pd.merge(df_deduped, gdf[['address', 'distance']], on='address', how='left')
    top3 = df_with_dist.nsmallest(3, 'distance')

    return top3[['date', 'address', 'adjusted_resale_price']], recent_1km

def get_block_transactions(postal_code, user_flat):
    # Validate postal code, if no match, hit error
    filtered = hdb_data[hdb_data['postal_code'].astype(str) == str(postal_code)]
    if filtered.empty:
        raise ValueError(f"Postal code {postal_code} not found in HDB dataset.") #if you want to hit error
        #return pd.DataFrame(columns=['date', 'address', 'adjusted_resale_price'])  #if you want empty df
    # Validate flat type, if no match, hit error
    flat_key = flat_map.get(user_flat.upper().strip())
    if not flat_key or flat_key not in trans_data.columns:
        raise ValueError(f"Unsupported or missing flat type '{user_flat}'") #if you want to hit error
        #return pd.DataFrame(columns=['date', 'address', 'adjusted_resale_price']) #if you want empty df

    # Filter transactions
    block_transaction = trans_data[trans_data['postal_code'].astype(str) == postal_code]
    block_same_type = block_transaction[block_transaction[flat_key] == 1]
    one_year_ago = datetime(2025, 1, 1) - timedelta(days=2*365)
    l_4months = datetime(2025, 1, 1) - timedelta(days=120)
    df_recent_year = block_same_type[block_same_type['date'] >= one_year_ago]
    df_recent_4m = block_same_type[block_same_type['date'] >= l_4months]
 
    top3_recent_year = df_recent_year.nlargest(3, 'date')
    top3_recent_4m = df_recent_4m.nlargest(3, 'date')

    return top3_recent_year[['date', 'address', 'adjusted_resale_price']], top3_recent_4m
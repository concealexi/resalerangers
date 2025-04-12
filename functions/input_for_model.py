from geopy.distance import geodesic
import pandas as pd

hdb_data = pd.read_csv("dataset/hdb_informations.csv")
schools = pd.read_csv("dataset/geocoded_schools.csv")
mrt_stations = pd.read_csv("dataset/mrt_stations.csv")
hawkercentres = pd.read_csv("dataset/hawkercentercoord.csv")

####################### FIXED VARIABLES ############################
cbd_coords = (1.287953, 103.851784)

options = ['flat_type_1 ROOM', 'flat_type_2 ROOM', 
            'flat_type_3 ROOM', 'flat_type_4 ROOM', 
            'flat_type_5 ROOM', 'flat_type_EXECUTIVE', 
            'flat_type_MULTI-GENERATION']

####################################################################

def get_all_nearest_amenities(coord_row):
    hdb_coords = (coord_row['latitude'], coord_row['longitude'])

    # Find nearest amenity and return name, distance, and coordinates
    def nearest_amenity(amenity_df, name_col, lat_col='latitude', lon_col='longitude'):
        min_dist = float('inf')
        nearest_name = None
        nearest_coords = (None, None)
        for row in amenity_df.itertuples(index=False):
            try:
                coords = (getattr(row, lat_col), getattr(row, lon_col))
                dist = geodesic(hdb_coords, coords).km
                if dist < min_dist:
                    min_dist = dist
                    nearest_name = getattr(row, name_col)
                    nearest_coords = coords
            except:
                continue
        return nearest_name, round(min_dist, 2), nearest_coords

    nearest_school, school_dist, school_coords = nearest_amenity(schools, 'school')
    nearest_mrt, mrt_dist, mrt_coords = nearest_amenity(mrt_stations, 'station_name')
    nearest_food, food_dist, food_coords = nearest_amenity(hawkercentres, 'hc_name')

    cbd_dist = round(geodesic(hdb_coords, cbd_coords).km, 2)

    return {
        'nearest_school': {
            'name': nearest_school,
            'distance_km': school_dist,
            'coords': school_coords
        },
        'nearest_mrt': {
            'name': nearest_mrt,
            'distance_km': mrt_dist,
            'coords': mrt_coords
        },
        'nearest_foodcourt': {
            'name': nearest_food,
            'distance_km': food_dist,
            'coords': food_coords
        },
        'distance_to_cbd': cbd_dist
    }


def check_floor(coord_row, floor): 
    max_floor = coord_row['max_floor_lvl']

    if floor > max_floor:
        raise ValueError(f"Floor {floor} does not exist for this property.")
    else: return floor


def check_flat(coord_row, user_flat):
    flat_key = f'flat_type_{user_flat}'
    if coord_row[flat_key] == 0: 
        raise ValueError(f"Flat type {user_flat} does not exist for this property.")
    
    else: return flat_key


def get_information(postal_code, flat_type, area, floor, remaining_lease):
    #get the postal code, and associated row
    coord_row = hdb_data[hdb_data['postal_code'] == postal_code].iloc[0]
    if coord_row.empty:
        raise ValueError(f"Postal code {postal_code} not found in coordinate dataset.")
    
    else:
        model_in = []

        amenities = get_all_nearest_amenities(coord_row)
        storey_median = check_floor(coord_row, floor)
        
        flat_cat = check_flat(coord_row, flat_type)
        encoded = {flat: 0 for flat in options}
        if flat_cat in encoded:
            encoded[flat_cat] = 1

        row = {
            'remaining_lease': remaining_lease,
            'min_dist_sch': amenities['nearest_school']['distance_km'], 
            'storey_median': storey_median, 
            'min_dist_mrt': amenities['nearest_mrt']['distance_km'],
            'floor_area_sqm': area, 
            'min_dist_cbd': amenities['distance_to_cbd']
        }
        row.update(encoded)
        model_in.append(row)

    
    return model_in

        






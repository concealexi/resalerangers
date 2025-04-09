import pandas as pd
hdb_df = pd.read_csv("dataset/hdb_informations.csv")
floor_percentiles = {
    'Low': 0.25,
    'Middle': 0.5,
    'High': 0.75
}

def get_floor_est(max_floor, floor_cat):        
    if floor_cat == 'Penthouse': 
        floor = max_floor
    elif floor_cat == 'Ground': 
        floor = 1
    else:
        proportion = floor_percentiles[floor_cat] 
        floor = round(max_floor * proportion)    

    return floor

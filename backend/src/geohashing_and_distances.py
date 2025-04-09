"""
will be getting 3 types of distances information 
1. nearest distance to a good school 
2. nearest distance to mrt (will use geohash to make it faster)
3. distance to cbd
"""

import pandas as pd
from geopy.distance import geodesic
from math import inf

# fixed datasets of the amenities will be put here
good_schools = pd.read_csv('../data/geocoded_schools.csv')
mrt_stations = pd.read_csv("../data/mrt_stations.csv")      # already done geohashing here to save some time
mrt_stations['date'] = pd.to_datetime(mrt_stations['date'])

cbd_coords = (1.287953, 103.851784)


# dist totop school
def dist_good_school(hdb_df):
    dist_sch = []

    for hdb_row in hdb_df.itertuples(index=False):
        hdb_coords = (hdb_row.latitude, hdb_row.longitude)
        min_dist = float(inf)

        for sch_row in good_schools.itertuples(index=False):
            sch_coords = (sch_row.latitude, sch_row.longitude)
            dist = geodesic(hdb_coords, sch_coords).km
            min_dist = min(min_dist, dist)

        dist_sch.append(min_dist)

    hdb_df["min_dist_sch"] = dist_sch
    return hdb_df


# distance to CBD area, which we define as the downtown core of SG
def dist_to_cbd(hdb_df):
    dist_cbd = []

    for hdb_row in hdb_df.itertuples(index=False):
        hdb_coords = (hdb_row.latitude, hdb_row.longitude)
        dist = geodesic(hdb_coords, cbd_coords).km

        dist_cbd.append(dist)

    hdb_df["min_dist_cbd"] = dist_cbd
    return hdb_df


# distance to nearest MRT, checking first for whether the MRT has opened 
def dist_nearest_mrt(hdb_df):

    nearest_mrt_dist = []
    #count = 0
    for hdb_row in hdb_df.itertuples(index=False):
        #count += 1
        #print(count)

        hdb_hash = hdb_row.geohash[:5]
        resale_date = hdb_row.date
        hdb_coords = (hdb_row.latitude, hdb_row.longitude)
        min_distance = float('inf')

        open_mrts = mrt_stations[mrt_stations['date'] <= resale_date]

        mrt_near = []
        for stn in open_mrts.itertuples(index=False):
            if stn.geohash[:5] == hdb_hash:
              mrt_near.append(stn)

        if len(mrt_near) == 0: filtered_mrts = open_mrts
        else: filtered_mrts = pd.DataFrame(mrt_near)

        #print(filtered_mrts)

        for mrt_row in filtered_mrts.itertuples(index=False):
            mrt_coords = (mrt_row.latitude, mrt_row.longitude)
            dist = geodesic(hdb_coords, mrt_coords).km
            min_distance = min(min_distance, dist)

        nearest_mrt_dist.append(min_distance)

    hdb_df["min_dist_mrt"] = nearest_mrt_dist
    return hdb_df


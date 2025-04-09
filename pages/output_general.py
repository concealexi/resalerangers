from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, no_update
import pandas as pd
from geopy.distance import geodesic
import dash_leaflet as dl
import dash_leaflet.express as dlx


register_page(__name__, path="/output-general")

# Constants
CBD_COORDS = (1.287953, 103.851784)

# Load data
hdb_df = pd.read_csv("dataset/hdb_final_dataset.csv")
schools_df = pd.read_csv("dataset/geocoded_schools.csv")
mrt_df = pd.read_csv("dataset/mrt_stations.csv")
hawker_df = pd.read_csv("dataset/hawkercentercoord.csv")

# Layout
layout = html.Div([
    dcc.Location(id='url'),

    html.H2("Your Selected Filters", style={'fontFamily': 'Helvetica', 'textAlign': 'center'}),

    html.Div(id='filter-summary', style={'width': '80%', 'margin': 'auto', 'marginBottom': '20px'}),

    html.H3("Recent Transactions Matching Your Filters", style={'textAlign': 'center'}),
    dcc.Store(id='selected-postal-store'),
    html.Div(id='filter-table'),

    html.Hr(),
    html.Div(id='property-details', style={'marginTop': '30px', 'width': '80%', 'margin': 'auto'}),
    html.Div([
        html.H3("Map of Nearby Amenities", style={
            'textAlign': 'center',
            'marginTop': '40px',
            'fontFamily': 'Helvetica'
        }),
        dl.Map(center=[1.3521, 103.8198], zoom=11, id='amenity-map', style={'width': '100%', 'height': '500px'}, children=[
            dl.TileLayer(),
            dl.LayerGroup(id='map-markers')
        ])
    ], style={'marginTop': '30px'})
])

# Utility function
def get_all_nearest_amenities(postal_code, hdb_amenities_dist_with_postal, geocoded_schools, mrt_stations, hawkercentrecoord):
    coord_row = hdb_amenities_dist_with_postal[hdb_amenities_dist_with_postal['postal_code'] == int(postal_code)]
    if coord_row.empty:
        return None

    hdb_coords = (coord_row.iloc[0]['latitude'], coord_row.iloc[0]['longitude'])

    def nearest_amenity(df, name_col, lat_col='latitude', lon_col='longitude'):
        nearest = None
        min_dist = float('inf')
        for row in df.itertuples(index=False):
            coords = (getattr(row, lat_col), getattr(row, lon_col))
            dist = geodesic(hdb_coords, coords).km
            if dist < min_dist:
                nearest = (getattr(row, name_col), round(dist, 2))
                min_dist = dist
        return nearest

    school = nearest_amenity(geocoded_schools, 'school')
    mrt = nearest_amenity(mrt_stations, 'station_name')
    hawker = nearest_amenity(hawkercentrecoord, 'hc_name')
    cbd_dist = round(geodesic(hdb_coords, CBD_COORDS).km, 2)

    return {
        'school': school,
        'mrt': mrt,
        'hawker': hawker,
        'cbd_dist': cbd_dist,
        'address': coord_row.iloc[0]['address']
    }

# Callback to filter and display table
@callback(
    Output('filter-table', 'children'),
    Output('selected-postal-store', 'data'),
    Input('user-filter-store', 'data'),
    Input('url', 'pathname'),
)
def update_table(filter_data, pathname):
    if pathname != "/output-general" or not filter_data:
        return html.Div("No data."), None

    town = filter_data.get('town')
    flat_type = filter_data.get('flat_type')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df = hdb_df[
        (hdb_df['town'] == town) &
        (hdb_df[flat_type_col] == 1)
    ]

    if lease:
        df = df[df['remaining_lease'] >= lease]
    if max_mrt:
        df = df[df['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df = df[df['min_dist_sch'] <= max_sch]

    df['address'] = df['block'].astype(str).str.strip() + " " + df['street_name'].str.title()
    df['Distance to MRT (km)'] = df['min_dist_mrt'].round(2)
    df['Distance to School (km)'] = df['min_dist_sch'].round(2)

    table_df = df[['address', 'adjusted_resale_price', 'month', 'postal_code', 'Distance to MRT (km)', 'Distance to School (km)']].rename(columns={
        'address': 'Address', 'adjusted_resale_price': 'Price (SGD)', 'month': 'Date Sold'
    })

    if table_df.empty:
        return html.Div("No results."), None

    return dash_table.DataTable(
        id='transaction-table',
        columns=[{"name": i, "id": i} for i in table_df.columns],
        data=table_df.to_dict('records'),
        row_selectable='single',
        style_cell={"textAlign": "left", "fontFamily": "Helvetica", "padding": "10px"},
        style_header={"fontWeight": "bold"},
        page_size=10
    ), table_df.iloc[0]['postal_code']  # default selection

# Callback to update details on click
@callback(
    Output('property-details', 'children'),
    Input('transaction-table', 'derived_virtual_selected_rows'),
    State('transaction-table', 'data')
)
def display_details(selected_rows, table_data):
    if not selected_rows or not table_data:
        return ""

    row = table_data[selected_rows[0]]
    postal = row['postal_code']
    result = get_all_nearest_amenities(postal, hdb_df, schools_df, mrt_df, hawker_df)

    if result is None:
        return html.Div("⚠️ Unable to retrieve details.")

    return html.Div([
        html.H4("🏠 Property details", style={'marginBottom': '20px'}),
        html.P(f"📍 {result['address']}"),
        html.P(f"🚇 Nearest MRT: {result['mrt'][0]} ({result['mrt'][1]} km)"),
        html.P(f"🎓 Nearest School: {result['school'][0]} ({result['school'][1]} km)"),
        html.P(f"🍜 Nearest Hawker Center: {result['hawker'][0]} ({result['hawker'][1]} km)"),
        html.P(f"🏙️ Distance to CBD: {result['cbd_dist']} km"),
    ], style={
        'fontFamily': 'Helvetica',
        'backgroundColor': '#fefefe',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'padding': '20px',
        'textAlign': 'left'
    })

@callback(
    Output('map-markers', 'children'),
    Input('transaction-table', 'derived_virtual_selected_rows'),
    State('transaction-table', 'data')
)
def update_map(selected_rows, table_data):
    if not selected_rows or not table_data:
        return []

    selected_row = table_data[selected_rows[0]]
    postal_code = selected_row.get("postal_code")

    if not postal_code:
        return []

    result = get_all_nearest_amenities(
        postal_code=int(postal_code),
        hdb_amenities_dist_with_postal=hdb_df,
        geocoded_schools=schools_df,
        mrt_stations=mrt_df,
        hawkercentrecoord=hawker_df
    )

    if result is None:
        return []

    hdb_row = hdb_df[hdb_df['postal_code'] == int(postal_code)]
    if hdb_row.empty:
        return []

    hdb_lat = hdb_row.iloc[0]['latitude']
    hdb_lon = hdb_row.iloc[0]['longitude']

    def find_coords(name, df, name_col):
        row = df[df[name_col] == name]
        if not row.empty:
            return row.iloc[0]['latitude'], row.iloc[0]['longitude']
        return None, None

    mrt_lat, mrt_lon = find_coords(result["mrt"][0], mrt_df, 'station_name')
    sch_lat, sch_lon = find_coords(result["school"][0], schools_df, 'school')
    hawker_lat, hawker_lon = find_coords(result["hawker"][0], hawker_df, 'hc_name')

    markers = []
    if hdb_lat and hdb_lon:
        markers.append(dl.Marker(position=[hdb_lat, hdb_lon], children=dl.Tooltip("🏠 HDB Location")))
    if mrt_lat and mrt_lon:
        markers.append(dl.Marker(position=[mrt_lat, mrt_lon], children=dl.Tooltip(f"🚇 MRT: {result['mrt'][0]} ({result['mrt'][1]} km)")))
    if sch_lat and sch_lon:
        markers.append(dl.Marker(position=[sch_lat, sch_lon], children=dl.Tooltip(f"🏫 School: {result['school'][0]} ({result['school'][1]} km)")))
    if hawker_lat and hawker_lon:
        markers.append(dl.Marker(position=[hawker_lat, hawker_lon], children=dl.Tooltip(f"🍜 Hawker: {result['hawker'][0]} ({result['hawker'][1]} km)")))

    return markers

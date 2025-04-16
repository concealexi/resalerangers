from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, no_update
import dash
import pandas as pd
from geopy.distance import geodesic
import dash_leaflet as dl
import dash_leaflet.express as dlx
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go



register_page(__name__, path="/output-general")

# Constants
CBD_COORDS = (1.287953, 103.851784)

# Load data
hdb_df = pd.read_csv("dataset/hdb_final_dataset.csv", dtype={"postal_code": str})
hdb_info = pd.read_csv("dataset/hdb_informations.csv", dtype={"postal_code": str})
schools_df = pd.read_csv("dataset/all_primary_schools.csv")
mrt_df = pd.read_csv("dataset/mrt_stations.csv")
hawker_df = pd.read_csv("dataset/hawkercentercoord.csv")


# Merge data
hdb_df['postal_code'] = hdb_df['postal_code'].astype(str).str.zfill(6)
hdb_info['postal_code'] = hdb_info['postal_code'].astype(str).str.zfill(6)
hdb_df = pd.merge(hdb_df, hdb_info[['postal_code', 'max_floor_lvl']], on='postal_code', how='left')
hdb_df = hdb_df[hdb_df['max_floor_lvl'].notna()]

town_chip_style = {
    "padding": "8px 20px",
    "border": "1.5px solid #7F0019",
    "borderRadius": "999px",
    "fontWeight": "600",
    "fontSize": "16px",
    "color": "#1A1A1A",
    "backgroundColor": "white"
}

icon_style = {
    "fontSize": "22px",
    "width": "30px"
}

label_style = {
    "fontSize": "16px",
    "marginLeft": "10px"
}

row_style = {
    "display": "flex",
    "alignItems": "center",
    "marginBottom": "12px"
}

# Icons for map

pinpoint_icon = {
    "iconUrl": "/assets/location_marker.svg",
    "iconSize": [30, 60]
}

MRT_icon = {
    "iconUrl": "/assets/mrt.svg",
    "iconSize": [20, 40]
}

sch_icon = {
    "iconUrl": "/assets/edu.svg",
    "iconSize": [30, 60]
}

hawker_icon = {
    "iconUrl": "/assets/utensil.svg",
    "iconSize": [25, 50]
}

layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='map-center-store', storage_type='memory'),
    html.Div(
        dcc.Link("< back to start", href="/", style={
            'fontFamily': 'Inter, sans-serif',
            'fontSize': '14px',
            'color': 'black',
            'textDecoration': 'none'
        }),
        style={
            'width': '100%',
            'textAlign': 'left',
            'marginLeft': '-270px',
            'marginTop': '40px',
            'marginBottom': '40px'
        }
    ),
    html.H3("You selected 2 towns", style={
        'fontFamily': 'Inter, sans-serif', 'textAlign': 'left'
    }),

    html.Div([
        html.Div([
            html.Img(
                src='assets/town.svg',
                style={
                    'width': '60px',
                    'height': '60px',
                    'marginRight': '12px',
                    'alignSelf': 'center'
                }
            )
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        }),

        html.Div([
            html.Div(id='town-filter', style={
                'padding': '8px 20px',
                'border': '1.5px solid #7F0019',
                'borderRadius': '999px',
                'fontWeight': '600',
                'fontSize': '16px',
                'color': '#1A1A1A',
                'backgroundColor': 'white',
                'marginRight': '10px'
            }),
            html.Div(id='town-filter-2', style={
                'padding': '8px 20px',
                'border': '1.5px solid #7F0019',
                'borderRadius': '999px',
                'fontWeight': '600',
                'fontSize': '16px',
                'color': '#1A1A1A',
                'backgroundColor': 'white'
            }),
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        })
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'left',
        'gap': '10px',
        'marginTop': '20px',
        'marginBottom': '20px',
        'fontFamily': 'Inter, sans-serif'
    }),

    html.H3("With features", style={
    'fontFamily': 'Inter, sans-serif', 'textAlign': 'left', 'marginBottom': '20px'
}),

    html.Div([
        html.Div([
          html.Div([
                html.Img(src='assets/flattype.svg', style={'width': '20px', 'marginRight': '10px', 'width': '30px',
                    'height': '30px'}),
                html.Span([
                    html.Strong("Flat Type: "),
                    html.Span(id='feature-filter-flat-type')
                ], style={"marginLeft": "10px"})
            ], style=row_style),
            html.Div([
                html.Img(src='assets/floorlevel.svg', style={'width': '20px', 'marginRight': '10px', 'width': '30px',
                    'height': '30px'}),
                html.Span([
                    html.Strong("Floor Level: "),
                    html.Span(id='feature-filter-floor')
                ], style={"marginLeft": "10px"})
            ], style=row_style),
            html.Div([
                html.Img(src='assets/lease.svg', style={'width': '20px', 'marginRight': '10px', 'width': '30px',
                    'height': '30px'}),
                html.Span([
                    html.Strong("Min Remaining Lease: "),
                    html.Span(id='feature-filter-lease')
                ], style={"marginLeft": "10px"})
            ], style=row_style)
        ], style={'flex': '1', 'marginBottom': '10px'}),

        html.Div([
            html.Div([
                html.Img(src='assets/mrt2.svg', style={'width': '20px', 'marginRight': '10px', 'width': '30px',
                    'height': '30px'}),
                html.Span([
                    html.Strong("Max Distance to MRT: "),
                    html.Span(id='feature-filter-mrt')
                ], style={"marginLeft": "10px"})
            ], style=row_style),
            html.Div([
                html.Img(src='assets/edu2.svg', style={'width': '20px', 'marginRight': '10px', 'width': '30px',
                    'height': '30px'}),
                html.Span([
                    html.Strong("Max Distance to Primary School: "),
                    html.Span(id='feature-filter-school')
                ], style={"marginLeft": "10px"})
            ], style=row_style)
        ], style={'flex': '1'})
    ], style={
        'display': 'flex', 'gap': '40px',
        'fontSize': '16px',
        'fontFamily': 'Inter, sans-serif'
    }),

    html.Div(id='bar-chart-section', children=[
        html.H3("Price trends for properties in the area", style={
            'textAlign': 'left', 'fontFamily': 'Inter, sans-serif', 'marginTop': '20px', 'fontSize' : '30px'
        }),
        html.P(id='bar-chart-subtitle', style={
            'textAlign': 'left', 'fontFamily': 'Inter, sans-serif',
            'fontSize': '16px', 'marginBottom': '10px'
        }),
        html.Div(id='bar-chart-subtitle', style={
            'marginBottom': '10px', 'textAlign': 'left',
            'fontFamily': 'Inter, sans-serif', 'fontSize': '16px'
        }),
    ]),

    html.Div([
        html.H4("Select which summary to view:", style={
            'fontFamily': 'Inter, sans-serif', 'marginBottom': '20px'
        }),
        dcc.RadioItems(
            id='summary-toggle',
            options=[],  # populated dynamically via callback
            value='town1',
            inline=True,
            className='mode-toggle-container',
            labelClassName='mode-toggle-label',
            inputClassName='mode-toggle-input'
        )
    ], style={
        'textAlign': 'left', 'marginTop': '20px',
        'marginBottom': '20px', 'fontFamily': 'Inter, sans-serif'
    }),

    html.Div([
        html.Div([
            dcc.Graph(id="quarterly-bar-chart", config={'displayModeBar': False}, style={"height": "100%", "width": "100%"})
        ], style={
            "flex": "7",
            "border": "1px solid lightgray",
            "padding": "20px",
            "borderRadius": "10px",
            "backgroundColor": "white",
            "height": "425px",
            "boxSizing": "border-box"
        }),

        html.Div(id="price-summary-container", style={
            "flex": "3",
            "border": "1px solid lightgray",
            "padding": "20px",
            "borderRadius": "10px",
            "fontFamily": "Inter, sans-serif",
            "backgroundColor": "#fff",
            "height": "425px",
            "boxSizing": "border-box"
        })
    ], style={
        "display": "flex",
        "gap": "20px",
        "maxWidth": "1000px",
        "margin": "0 auto",
        "marginTop": "20px",
        "alignItems": "stretch"
    }),

    html.Div([
            html.H3("Most Popular Blocks in the Past Year", style={
                'textAlign': 'left',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '28px',
                'marginTop': '40px',
                'marginBottom': '8px'
            }),
            html.P("For properties that match your selected filters", style={
                'textAlign': 'left',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '16px',
                'color': '#555',
                'marginBottom': '30px'
            }),

            html.Div([
                html.Div([
                    html.H4(id='town1-name', style={
                        'fontWeight': 'bold',
                        'textAlign': 'left',
                        'fontSize': '20px',
                        'fontFamily': 'Inter, sans-serif',
                        'marginBottom': '10px'
                    }),dash_table.DataTable(
                        id='transaction-table-town1', 
                        columns=[], 
                        data=[],     
                        style_table={'display': 'none'} 
                    ),
                    html.Div(id='filter-table-town1')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                html.Div([
                    html.H4(id='town2-name', style={
                        'fontWeight': 'bold',
                        'textAlign': 'left',
                        'fontSize': '20px',
                        'fontFamily': 'Inter, sans-serif',
                        'marginBottom': '10px'
                    }),dash_table.DataTable(
                        id='transaction-table-town2',
                        columns=[],
                        data=[],
                        style_table={'display': 'none'}
                    ),
                    html.Div(id='filter-table-town2')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
            ])
        ]),

    dcc.Store(id='selected-postal-store'),
    dcc.Store(id='selected-postal-store-town2'),

    html.Hr(),

    html.Div([
        html.Div([
            html.H3("Property details", style={
                'fontWeight': 'bold',
                'textAlign': 'left',
                'fontSize': '20px',
                'fontFamily': 'Inter, sans-serif',
                'marginBottom': '10px'
            }),
            html.Div(id='property-amenities-container')
        ], style={
            "flex": 1,
            "border": "1px solid lightgray",
            "padding": "20px",
            "borderRadius": "10px",
            "backgroundColor": "white",
            "fontFamily": "Inter, sans-serif",
            "boxSizing": "border-box"
        }),

        html.Div([
            html.H3("Property details", style={
                'fontWeight': 'bold',
                'textAlign': 'left',
                'fontSize': '20px',
                'fontFamily': 'Inter, sans-serif',
                'marginBottom': '10px'
            }),
            html.Div(id='property-amenities-container-town2')
        ], style={
            "flex": 1,
            "border": "1px solid lightgray",
            "padding": "20px",
            "borderRadius": "10px",
            "backgroundColor": "white",
            "fontFamily": "Inter, sans-serif",
            "boxSizing": "border-box"
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'center',
        'alignItems': 'stretch', 
        'width': '100%',
        'gap': '20px',
        'marginTop': '30px'
    }),
    html.Div([
        html.H3("Map of Nearby Amenities", style={
            'textAlign': 'Left',
            'marginTop': '40px',
            'fontFamily': 'Inter, sans-serif', 'marginBottom' : '40px',
            'fontSize' : '24px'
        }),
        html.Div([
            html.Div([
                dl.Map(id='amenity-map',
                       center=[1.287953, 103.851784],
                       zoom=15,
                       children=[
                           dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                        attribution='&copy; <a href="https://carto.com/">CartoDB</a>'),
                           dl.LayerGroup(id='map-markers')
                       ],
                       style={'width': '100%', 'height': '400px'})
            ], style={'flex': '1', 'marginRight': '10px'}),

            html.Div([
                dl.Map(id='amenity-map-town2',
                       center=[1.287953, 103.851784],
                       zoom=15,
                       children=[
                           dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                        attribution='&copy; <a href="https://carto.com/">CartoDB</a>'),
                           dl.LayerGroup(id='map-markers-town2')
                       ],
                       style={'width': '100%', 'height': '400px'})
            ], style={'flex': '1', 'marginLeft': '10px'})
        ], style={
            'display': 'flex', 'gap': '20px',
            'width': '100%'
        })
    ], style={'marginTop': '30px'})

], style={  
    'maxWidth': '1000px',
    'margin': '0 auto', 'marginBottom': '40px'
})


# Utility function
def get_all_nearest_amenities(postal_code, hdb_amenities_dist_with_postal, all_primary_schools, mrt_stations, hawkercentrecoord):
    coord_row = hdb_amenities_dist_with_postal[hdb_amenities_dist_with_postal['postal_code'] == postal_code]
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

    school = nearest_amenity(all_primary_schools, 'school')
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

def generate_map_markers(postal_code):
    result = get_all_nearest_amenities(postal_code, hdb_df, schools_df, mrt_df, hawker_df)
    if result is None:
        raise dash.exceptions.PreventUpdate

    hdb_row = hdb_df[hdb_df['postal_code'] == postal_code]
    if hdb_row.empty:
        raise dash.exceptions.PreventUpdate

    hdb_lat = hdb_row.iloc[0]['latitude']
    hdb_lon = hdb_row.iloc[0]['longitude']

    def find_coords(name, df, name_col):
        row = df[df[name_col] == name]
        return (row.iloc[0]['latitude'], row.iloc[0]['longitude']) if not row.empty else (None, None)

    mrt_lat, mrt_lon = find_coords(result["mrt"][0], mrt_df, 'station_name')
    sch_lat, sch_lon = find_coords(result["school"][0], schools_df, 'school')
    hawker_lat, hawker_lon = find_coords(result["hawker"][0], hawker_df, 'hc_name')

    markers = []
    if hdb_lat and hdb_lon:
        markers.append(dl.Marker(position=[hdb_lat, hdb_lon], icon=pinpoint_icon, children=dl.Tooltip("🏠 HDB Location")))
    if mrt_lat and mrt_lon:
        markers.append(dl.Marker(position=[mrt_lat, mrt_lon], icon = MRT_icon,children=dl.Tooltip(f"🚇 MRT: {result['mrt'][0]} ({result['mrt'][1]} km)")))
    if sch_lat and sch_lon:
        markers.append(dl.Marker(position=[sch_lat, sch_lon], icon = sch_icon, children=dl.Tooltip(f"🏫 School: {result['school'][0]} ({result['school'][1]} km)")))
    if hawker_lat and hawker_lon:
        markers.append(dl.Marker(position=[hawker_lat, hawker_lon], icon = hawker_icon, children=dl.Tooltip(f"🍜 Hawker: {result['hawker'][0]} ({result['hawker'][1]} km)")))

    return markers, [hdb_lat, hdb_lon]

@callback(
    Output('quarterly-bar-chart', 'figure'),
    Output('price-summary-container', 'children'),
    Output('bar-chart-subtitle', 'children'),
    Output('town-filter', 'children'),
    Output('town-filter-2', 'children'),  # ✅ Add this line
    Output('feature-filter-flat-type', 'children'),
    Output('feature-filter-floor', 'children'),
    Output('feature-filter-lease', 'children'),
    Output('feature-filter-mrt', 'children'),
    Output('feature-filter-school', 'children'),
    Input('user-filter-store', 'data'),
    Input('summary-toggle', 'value')
)

def update_quarterly_chart(filter_data, summary_toggle):
    if not filter_data:
        raise dash.exceptions.PreventUpdate

    df = hdb_df.copy()
    town = filter_data.get('town1')
    town2 = filter_data.get('town2')
    town = town or "Town 1"
    town2 = town2 or "Town 2"
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df1 = df[(df['town'] == town) & (df[flat_type_col] == 1)].copy()
    df2 = df[(df['town'] == town2) & (df[flat_type_col] == 1)].copy()

    for dfx in [df1, df2]:
        dfx['storey_median'] = pd.to_numeric(dfx['storey_median'], errors='coerce')
        dfx['low_threshold'] = (dfx['max_floor_lvl'] * 0.25).round()
        dfx['high_threshold'] = (dfx['max_floor_lvl'] * 0.75).round()

        def classify_floor(row):
            if pd.isna(row['storey_median']) or pd.isna(row['max_floor_lvl']):
                return None
            if row['storey_median'] <= row['low_threshold']:
                return "Low"
            elif row['storey_median'] > row['high_threshold']:
                return "High"
            else:
                return "Medium"

        dfx['floor_category'] = dfx.apply(classify_floor, axis=1)

    if floor_level:
        df1 = df1[df1['floor_category'] == floor_level]
        df2 = df2[df2['floor_category'] == floor_level]
    if lease:
        df1 = df1[df1['remaining_lease'] >= lease]
        df2 = df2[df2['remaining_lease'] >= lease]
    if max_mrt:
        df1 = df1[df1['min_dist_mrt'] <= max_mrt]
        df2 = df2[df2['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df1 = df1[df1['min_dist_sch'] <= max_sch]
        df2 = df2[df2['min_dist_sch'] <= max_sch]

    months = [f"{y}-{m:02d}" for y in [2024, 2025] for m in range(1, 13)][3:15]
    month_to_q = {m: f"Q{((int(m[5:7]) - 1) // 3) + 1} {m[:4]}" for m in months}

    df1 = df1[df1['month'].isin(months)]
    df2 = df2[df2['month'].isin(months)]
    df1['Quarter'] = df1['month'].map(month_to_q)
    df2['Quarter'] = df2['month'].map(month_to_q)

    def compute_q_avg(df, town_label):
        quarters = ['Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025']
        if df.empty:
            return pd.DataFrame({
                'Quarter': quarters,
                'adjusted_resale_price': [0] * len(quarters),
                'units_sold': [0] * len(quarters),
                'Town': [town_label] * len(quarters)
            }), None
        else:
            q_avg = df.groupby('Quarter').agg(
                adjusted_resale_price=('adjusted_resale_price', 'mean'),
                units_sold=('adjusted_resale_price', 'count')
            ).fillna(0).round().reset_index()
            q_avg['Quarter'] = pd.Categorical(q_avg['Quarter'], quarters, ordered=True)
            q_avg = q_avg.sort_values('Quarter')
            q_avg['Town'] = town_label
            return q_avg, df


    q_avg1, df1_valid = compute_q_avg(df1, town.title())
    q_avg2, df2_valid = compute_q_avg(df2, town2.title())
    combined_avg = pd.concat([q_avg1, q_avg2])

    color_map = {
        town.title(): "#7F0019",
        town2.title(): "#e6ab2d"
    }

    fig = go.Figure()

    for town_name in [town.title(), town2.title()]:
        df_town = combined_avg[combined_avg['Town'] == town_name]

        fig.add_trace(go.Bar(
            x=df_town['Quarter'],
            y=df_town['adjusted_resale_price'],
            name=town_name,
            marker=dict(color=color_map[town_name]),
            customdata=df_town[['units_sold']],
            width=0.3,
            hovertemplate=(
                "In %{x}<br>" +
                "%{customdata[0]} units sold<br>" +
                "Average: $%{y:,.0f}<extra></extra>"
            )
        ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.17,
            xanchor="center",
            x=0.5,
            font=dict(size=13)
        ),
        yaxis=dict(title="", tickformat=",", showgrid=True, zeroline=True, zerolinecolor='lightgray'),
        xaxis=dict(title="", showgrid=False),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        title=None,
        hoverlabel=dict(
            font=dict(family="Inter, sans-serif", size=14, color="#333"),
            bgcolor="white",
            bordercolor="#ddd",
            align="left"
        )
    )

    def build_summary(df, town_name):
        if df is None or df.empty:
            return html.Div("No data available.")
        avg = int(df['adjusted_resale_price'].mean())
        max_row = df.loc[df['adjusted_resale_price'].idxmax()]
        min_row = df.loc[df['adjusted_resale_price'].idxmin()]
        max_month = datetime.strptime(max_row['month'], "%Y-%m").strftime("%b %Y")
        min_month = datetime.strptime(min_row['month'], "%Y-%m").strftime("%b %Y")
        return html.Div([
            html.H2(town_name),
            html.H4("Average Price", style={"fontSize": "18px", "marginBottom": "5px", "fontStyle":"italic"}),
            html.P(f"${avg:,}", style={"fontSize": "20px", "fontWeight": "bold", "marginBottom": "20px"}),
            html.H4("Highest Sold", style={"fontSize": "16px", "marginBottom": "5px"}),
            html.P(f"${int(max_row['adjusted_resale_price']):,}", style={"fontSize": "18px", "fontWeight": "bold", "margin": "0"}),
            html.P(f"{max_row['address']}", style={"fontSize": "14px", "margin": "0", "fontStyle":"italic"}),
            html.P(f"{max_month}", style={"fontSize": "14px", "marginBottom": "20px"}),
            html.H4("Lowest Sold", style={"fontSize": "16px", "marginBottom": "5px"}),
            html.P(f"${int(min_row['adjusted_resale_price']):,}", style={"fontSize": "18px", "fontWeight": "bold", "margin": "0"}),
            html.P(f"{min_row['address']}", style={"fontSize": "14px", "margin": "0", "fontStyle":"italic"}),
            html.P(f"{min_month}", style={"fontSize": "14px", "fontStyle": "italic"})
        ], style={
            "padding": "20px",
            "fontFamily": "Inter, sans-serif"
        })

    summary1 = build_summary(df1_valid, town.title())
    summary2 = build_summary(df2_valid, town2.title())
    subtitle = f"Based on flats in {town.title()} and {town2.title()} with {flat_type.title()} flat type and same amenity features"
    selected_summary = summary1 if summary_toggle == 'town1' else summary2

    # Return plain text values
    return (
        fig,
        selected_summary,
        subtitle,
        f"{town.title()}",
        f"{town2.title()}",
        f"{flat_type}",
        f"{floor_level}",
        f"{lease} years" if lease else "",
        f"{max_mrt} km" if max_mrt else "",
        f"{max_sch} km" if max_sch else ""
    )

# Callback to filter and display table
@callback(
    Output('filter-table-town1', 'children'),
    Output('selected-postal-store', 'data'),
    Output('transaction-table-town1', 'active_cell'),
    Input('user-filter-store', 'data'),
    Input('url', 'pathname'),
)
def update_table(filter_data, pathname):
    if pathname != "/output-general" or not filter_data:
        return html.Div("No data."), None, None

    town = filter_data.get('town1')
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df = hdb_df[
        (hdb_df['town'] == town) &
        (hdb_df[flat_type_col] == 1)
    ].copy()

    # Floor level classification
    df['storey_median'] = pd.to_numeric(df['storey_median'], errors='coerce')
    df['low_threshold'] = (df['max_floor_lvl'] * 0.25).round()
    df['high_threshold'] = (df['max_floor_lvl'] * 0.75).round()

    def classify_floor(row):
        if pd.isna(row['storey_median']) or pd.isna(row['max_floor_lvl']):
            return None
        if row['storey_median'] <= row['low_threshold']:
            return "Low"
        elif row['storey_median'] > row['high_threshold']:
            return "High"
        else:
            return "Medium"

    df['floor_category'] = df.apply(classify_floor, axis=1)

    # Apply filters
    if floor_level:
        df = df[df['floor_category'] == floor_level]
    if lease:
        df = df[df['remaining_lease'] >= lease]
    if max_mrt:
        df = df[df['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df = df[df['min_dist_sch'] <= max_sch]

    # Create address field
    df['address'] = df['block'].astype(str).str.strip() + " " + df['street_name'].str.title()

    # Filter to transactions from last year only
    valid_months = [f"{y}-{m:02d}" for y in [2024, 2025] for m in range(1, 13)][3:15]  # Apr 2024 to Mar 2025
    df = df[df['month'].isin(valid_months)]

    # Group and aggregate for summary table
    summary_df = df.groupby('address').agg(
        num_transactions=('adjusted_resale_price', 'count'),
        min_price=('adjusted_resale_price', 'min'),
        max_price=('adjusted_resale_price', 'max')
    ).reset_index()


    summary_df['Price Range'] = summary_df.apply(
    lambda row: (
        f"${int(row['min_price']):,} - ${int(row['max_price']):,}"
        if pd.notna(row['min_price']) and pd.notna(row['max_price'])
        else "N/A"
    ),
    axis=1
    )


    summary_df = summary_df.rename(columns={
        'address': 'Address',
        'num_transactions': 'Units Sold'
    })[['Address', 'Units Sold', 'Price Range']]

    summary_df = summary_df.sort_values(by='Units Sold', ascending=False).head(10)

    if summary_df.empty:
        return html.Div("No results."), None, None

    return dash_table.DataTable(
        id='transaction-table-town1',
        columns=[{"name": i, "id": i} for i in summary_df.columns],
        data=summary_df.to_dict('records'),
        cell_selectable=True,
        active_cell={'row': 0, 'column': 0, 'column_id': summary_df.columns[0]},
        style_cell={
            'fontFamily': 'Inter, sans-serif',
            'textAlign': 'left',
            'padding': '16px',
            'border': 'none',
            'fontSize': '15px',
            'backgroundColor': '#f9f9f9',
        },
        style_header={
            'backgroundColor': '#ffffff',
            'fontWeight': 'bold',
            'borderBottom': '2px solid #dddddd',
            'fontSize': '16px',
        },
        style_table={
            'width': '100%',
            'marginTop': '10px',
            'borderCollapse': 'separate',
            'borderSpacing': '0 8px'
        },
        page_size=10
    ), df.to_dict('records'), {'row': 0, 'column': 0, 'column_id': summary_df.columns[0]}



@callback(
    Output('filter-table-town2', 'children'),
    Output('selected-postal-store-town2', 'data'),
    Output('transaction-table-town2', 'active_cell'),
    Input('user-filter-store', 'data'),
    Input('url', 'pathname'),
)
def update_table_town2(filter_data, pathname):
    if pathname != "/output-general" or not filter_data or not filter_data.get("town2"):
        return html.Div("No data."), None, None

    town2 = filter_data.get('town2')
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df = hdb_df[
        (hdb_df['town'] == town2) &
        (hdb_df[flat_type_col] == 1)
    ].copy()

    df['storey_median'] = pd.to_numeric(df['storey_median'], errors='coerce')
    df['low_threshold'] = (df['max_floor_lvl'] * 0.25).round()
    df['high_threshold'] = (df['max_floor_lvl'] * 0.75).round()

    def classify_floor(row):
        if pd.isna(row['storey_median']) or pd.isna(row['max_floor_lvl']):
            return None
        if row['storey_median'] <= row['low_threshold']:
            return "Low"
        elif row['storey_median'] > row['high_threshold']:
            return "High"
        else:
            return "Medium"

    df['floor_category'] = df.apply(classify_floor, axis=1)

    if floor_level:
        df = df[df['floor_category'] == floor_level]
    if lease:
        df = df[df['remaining_lease'] >= lease]
    if max_mrt:
        df = df[df['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df = df[df['min_dist_sch'] <= max_sch]

    df['address'] = df['block'].astype(str).str.strip() + " " + df['street_name'].str.title()

    # Filter to last year
    valid_months = [f"{y}-{m:02d}" for y in [2024, 2025] for m in range(1, 13)][3:15]
    df = df[df['month'].isin(valid_months)]

    summary_df = df.groupby('address').agg(
        num_transactions=('adjusted_resale_price', 'count'),
        min_price=('adjusted_resale_price', 'min'),
        max_price=('adjusted_resale_price', 'max')
    ).reset_index()

    summary_df['Price Range'] = summary_df.apply(
    lambda row: (
        f"${int(row['min_price']):,} - ${int(row['max_price']):,}"
        if pd.notna(row['min_price']) and pd.notna(row['max_price'])
        else "N/A"
    ),
    axis=1
    )


    summary_df = summary_df.rename(columns={
        'address': 'Address',
        'num_transactions': 'Units Sold'
    })[['Address', 'Units Sold', 'Price Range']]

    summary_df = summary_df.sort_values(by='Units Sold', ascending=False).head(10)


    if summary_df.empty:
        return html.Div("No results."), None, None

    return dash_table.DataTable(
        id='transaction-table-town2',
        columns=[{"name": i, "id": i} for i in summary_df.columns],
        data=summary_df.to_dict('records'),
        cell_selectable=True,
        active_cell={'row': 0, 'column': 0, 'column_id': summary_df.columns[0]},
        style_cell={
            'fontFamily': 'Inter, sans-serif',
            'textAlign': 'left',
            'padding': '16px',
            'border': 'none',
            'fontSize': '15px',
            'backgroundColor': '#f9f9f9',
        },
        style_header={
            'backgroundColor': '#ffffff',
            'fontWeight': 'bold',
            'borderBottom': '2px solid #dddddd',
            'fontSize': '16px',
        },
        style_table={
            'width': '100%',
            'marginTop': '10px',
            'borderCollapse': 'separate',
            'borderSpacing': '0 8px'
        },
        selected_rows=[],
        page_size=10
    ), df.to_dict('records'),  {'row': 0, 'column': 0, 'column_id': summary_df.columns[0]}

def make_amenity(icon, title, value):
    return html.Div([
        html.Img(src=f"/assets/{icon}", style={
            "width": "45px", "height": "45px", "marginRight": "12px", "flexShrink": "0", "marginTop": "2px"
        }),
        html.Div([
            html.Div(title, style={
                "fontWeight": "600", "fontSize": "15px", "marginBottom": "2px"
            }),
            html.Div(value, style={
                "fontSize": "14px", "color": "#333"
            })
        ])
    ], style={
        "display": "flex", "alignItems": "flex-start", "marginBottom": "20px"
    })

# Callback to update details on click
@callback(
    Output('property-amenities-container', 'children'),
    Input('transaction-table-town1', 'active_cell'),
    State('transaction-table-town1', 'data'),
    State('selected-postal-store', 'data')
)
def display_details_split(active_cell, table_data, original_data):
    if not active_cell or not table_data or not original_data:
        return "No data."

    selected_address = table_data[active_cell['row']]['Address']

    for row in original_data:
        if row['address'] == selected_address:
            postal = row['postal_code']
            break
    else:
        return html.Div("⚠️ Address not found")

    result = get_all_nearest_amenities(postal, hdb_df, schools_df, mrt_df, hawker_df)
    if result is None:
        return html.Div("⚠️ Unable to retrieve details.")

    amenities = [
        make_amenity("location_marker.svg", "Address", result['address']),
        make_amenity("mrt.svg", "Nearest MRT", f"{result['mrt'][0]}, {result['mrt'][1]} km"),
        make_amenity("edu.svg", "Nearest Primary School", f"{result['school'][0]}, {result['school'][1]} km"),
        make_amenity("utensil.svg", "Nearest Hawker Center", f"{result['hawker'][0]}, {result['hawker'][1]} km"),
        make_amenity("city.svg", "Distance to CBD", f"{result['cbd_dist']} km")
    ]
    return amenities


@callback(
    Output('property-amenities-container-town2', 'children'),
    Input('transaction-table-town2', 'active_cell'),
    State('transaction-table-town2', 'data'),
    State('selected-postal-store-town2', 'data')
)
def display_details_split_town2(active_cell, table_data, original_data):
    if not active_cell or not table_data or not original_data:
        return "No data."

    selected_address = table_data[active_cell['row']]['Address']

    for row in original_data:
        if row['address'] == selected_address:
            postal = row['postal_code']
            break
    else:
        return html.Div("⚠️ Address not found")

    result = get_all_nearest_amenities(postal, hdb_df, schools_df, mrt_df, hawker_df)
    if result is None:
        return html.Div("⚠️ Unable to retrieve details.")

    amenities = [
        make_amenity("location_marker.svg", "Address", result['address']),
        make_amenity("mrt.svg", "Nearest MRT", f"{result['mrt'][0]}, {result['mrt'][1]} km"),
        make_amenity("edu.svg", "Nearest Primary School", f"{result['school'][0]}, {result['school'][1]} km"),
        make_amenity("utensil.svg", "Nearest Hawker Center", f"{result['hawker'][0]}, {result['hawker'][1]} km"),
        make_amenity("city.svg", "Distance to CBD", f"{result['cbd_dist']} km")
    ]
    return amenities

@callback(
    Output('map-markers', 'children'),
    Output('amenity-map', 'center'),
    Input('transaction-table-town1', 'active_cell'),
    State('transaction-table-town1', 'data'),
    State('selected-postal-store', 'data')
)
def update_map_and_center(active_cell, table_data, original_data):
    if not active_cell or not table_data or not original_data:
        raise dash.exceptions.PreventUpdate

    selected_address = table_data[active_cell['row']]['Address']
    for row in original_data:
        if row['address'] == selected_address:
            postal_code = str(row['postal_code']).zfill(6)
            break
    else:
        raise dash.exceptions.PreventUpdate

    return generate_map_markers(postal_code)

@callback(
    Output('map-markers-town2', 'children'),
    Output('amenity-map-town2', 'center'),
    Input('transaction-table-town2', 'active_cell'),
    State('transaction-table-town2', 'data'),
    State('selected-postal-store-town2', 'data')
)
def update_map_and_center_town2(active_cell, table_data, original_data):
    if not active_cell or not table_data or not original_data:
        raise dash.exceptions.PreventUpdate

    selected_address = table_data[active_cell['row']]['Address']
    for row in original_data:
        if row['address'] == selected_address:
            postal_code = str(row['postal_code']).zfill(6)
            break
    else:
        raise dash.exceptions.PreventUpdate

    return generate_map_markers(postal_code)

@callback(
    Output('transaction-table-town1', 'style_data_conditional'),
    Input('transaction-table-town1', 'active_cell')
)
def style_active_row_town1(active_cell):
    style = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#fcfcfc',
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#f9f9f9',
        }
    ]
    if active_cell:
        row_idx = active_cell['row']
        style.append({
            'if': {'row_index': row_idx},
            'backgroundColor': '#7F0019',
            'color': 'white',
            'borderTop': '2px solid #dddddd'
        })
    return style

@callback(
    Output('transaction-table-town2', 'style_data_conditional'),
    Input('transaction-table-town2', 'active_cell')
)
def style_active_row_town2(active_cell):
    style = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#fcfcfc',
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#f9f9f9',
        }
    ]
    if active_cell:
        row_idx = active_cell['row']
        style.append({
            'if': {'row_index': row_idx},
            'backgroundColor': '#7F0019',
            'color': 'white',
            'borderTop': '2px solid #dddddd'
        })
    return style

@callback(
    Output('summary-toggle', 'options'),
    Output('summary-toggle', 'value'),
    Input('user-filter-store', 'data'),
)
def update_toggle_options(filter_data):
    if not filter_data:
        raise dash.exceptions.PreventUpdate

    town1 = filter_data.get('town1', 'Town 1')
    town2 = filter_data.get('town2', 'Town 2')

    options = [{'label': f'{town1.title()} ', 'value': 'town1'}]
    if town2:
        options.append({'label': f'{town2.title()} ', 'value': 'town2'})

    return options, 'town1'

@callback(
    Output('town1-name', 'children'),
    Output('town2-name', 'children'),
    Input('user-filter-store', 'data'),
)
def update_town_titles(filter_data):
    town1 = filter_data.get('town1', 'Town 1') if filter_data else 'Town 1'
    town2 = filter_data.get('town2', 'Town 2') if filter_data else 'Town 2'
    return town1.title(), town2.title()


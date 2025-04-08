from dash import html, dcc, register_page, callback, Output, Input, State
import pandas as pd
import dash_leaflet as dl

# Load and merge data
hdb_df = pd.read_csv("dataset/hdb_final_dataset.csv")
hdb_info = pd.read_csv("dataset/hdb_informations.csv")
hdb_df = pd.merge(hdb_df, hdb_info[['postal_code', 'max_floor_lvl']], on='postal_code', how='left')

# Preprocess: get unique towns and map postal codes by town
towns = sorted(hdb_df['town'].dropna().unique())
town_postal_map = hdb_df.groupby('town')['postal_code'].apply(list).to_dict()

register_page(__name__, path="/input-general")

layout = html.Div([
    dcc.Store(id='user-filter-store'),

    html.H2("What property are you looking for?", style={
        'fontFamily': 'Helvetica', 'textAlign': 'center', 'marginBottom': '10px'
    }),
    html.H4("Please fill in the characteristics for the flat of your choice", style={
        'fontFamily': 'Helvetica', 'textAlign': 'center', 'marginBottom': '30px'
    }),

    html.Div([

        html.Label("Town", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='newbie-town-dropdown',
            options=[{'label': town.title(), 'value': town} for town in towns],
            placeholder="Enter a town",
            style={'marginBottom': '5px', 'fontFamily': 'Helvetica'}
        ),
        html.P("Looking to compare towns? You may select up to 2 to view!", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Helvetica',
            'marginBottom': '20px'
        }),

        html.Label("Flat Type", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='newbie-flat-type',
            options=[],
            placeholder='Enter flat type',
            style={'marginBottom': '25px', 'fontFamily': 'Helvetica'}
        ),

        html.Label("Floor Level", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='newbie-floor-level',
            options=[],
            placeholder='Enter floor level',
            style={'marginBottom': '40px', 'fontFamily': 'Helvetica'}
        ),

        html.H4("You may also add additional filters for your search!", style={
            'fontFamily': 'Helvetica', 'marginBottom': '30px'
        }),

        html.Label("Minimum Remaining Lease", style={'fontFamily': 'Helvetica'}),
        dcc.Slider(
            id='newbie-lease',
            min=0,
            max=99,
            step=1,
            tooltip={'always_visible': False, 'placement': 'bottom'},
            marks={0: '0', 99: '99 years'},
        ),
        html.P("Select a minimum remaining lease year", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Helvetica',
            'marginBottom': '30px'
        }),

        html.Label("Distance to an MRT", style={'fontFamily': 'Helvetica'}),
        dcc.Slider(
            id='newbie-dist-mrt',
            min=0,
            max=2.5,
            step=0.1,
            tooltip={'always_visible': False, 'placement': 'bottom'},
            marks={0: '0', 2.5: '2.5km'},
        ),
        html.P("Select a maximum distance from the nearest available MRT", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Helvetica',
            'marginBottom': '30px'
        }),

        html.Label("Distance to a School", style={'fontFamily': 'Helvetica'}),
        dcc.Slider(
            id='newbie-dist-school',
            min=0,
            max=2,
            step=0.1,
            tooltip={'always_visible': False, 'placement': 'bottom'},
            marks={0: '0', 2: '2km'},
        ),
        html.P("Select a maximum distance from the nearest available school", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Helvetica',
            'marginBottom': '30px'
        }),

        html.Div([
            html.Button("Submit", id="newbie-submit", n_clicks=0, style={
                'backgroundColor': '#ff963b',
                'color': 'white',
                'padding': '10px 20px',
                'border': '2px solid #e67e22',
                'borderRadius': '8px',
                'fontSize': '16px',
                'cursor': 'pointer',
                'fontFamily': 'Helvetica'
            })
        ], style={
            'border': '2px solid #ccc',
            'padding': '10px',
            'borderRadius': '12px',
            'backgroundColor': '#fffaf3',
            'textAlign': 'center',
            'width': 'fit-content',
            'margin': '0 auto',
            'fontFamily': 'Helvetica'
        }),

        html.Div(id='newbie-output', style={'marginTop': '30px', 'fontFamily': 'Helvetica'})
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '40px', 'fontFamily': 'Helvetica'})
])

# CALLBACKS

@callback(
    Output('newbie-flat-type', 'options'),
    Input('newbie-town-dropdown', 'value')
)
def update_flat_type_options(town):
    if not town:
        return []

    filtered = hdb_df[hdb_df['town'] == town]
    flat_type_cols = [
        'flat_type_1 ROOM', 'flat_type_2 ROOM', 'flat_type_3 ROOM',
        'flat_type_4 ROOM', 'flat_type_5 ROOM',
        'flat_type_EXECUTIVE', 'flat_type_MULTI-GENERATION'
    ]

    type_counts = filtered[flat_type_cols].sum()

    return [
        {'label': col.replace('flat_type_', '').replace('_', ' ').title(), 'value': col.replace('flat_type_', '')}
        for col, val in type_counts.items() if val > 0
    ]

@callback(
    Output('newbie-floor-level', 'options'),
    Input('newbie-town-dropdown', 'value'),
    Input('newbie-flat-type', 'value')
)
def update_floor_categories(town, flat_type):
    if not town or not flat_type:
        return []

    flat_col = f"flat_type_{flat_type.upper()}"
    filtered = hdb_df[
        (hdb_df['town'] == town) &
        (hdb_df[flat_col] == 1)
    ]

    if filtered.empty:
        return []

    try:
        max_floor = int(filtered['max_floor_lvl'].dropna().mode()[0])
    except:
        return []

    low = list(range(1, int(round(max_floor * 0.25)) + 1))
    medium = list(range(int(round(max_floor * 0.25)) + 1, int(round(max_floor * 0.75)) + 1))
    high = list(range(int(round(max_floor * 0.75)) + 1, max_floor + 1))

    return [
        {'label': f"Low (Floors {low[0]:02d}–{low[-1]:02d})", 'value': 'Low'},
        {'label': f"Medium (Floors {medium[0]:02d}–{medium[-1]:02d})", 'value': 'Medium'},
        {'label': f"High (Floors {high[0]:02d}–{high[-1]:02d})", 'value': 'High'}
    ]

@callback(
    Output('newbie-output', 'children'),
    Output('newbie-marker', 'position'),
    Output('newbie-popup', 'children'),
    Input('newbie-submit', 'n_clicks'),
    State('newbie-town-dropdown', 'value'),
    State('newbie-flat-type', 'value'),
    State('newbie-floor-level', 'value'),
    prevent_initial_call=True
)
def display_result(n_clicks, town, flat_type, floor_level):
    if not town or not flat_type or not floor_level:
        return html.Div("Please complete all required fields."), [1.3521, 103.8198], "No location selected."

    flat_col = f"flat_type_{flat_type.upper()}"
    filtered = hdb_df[
        (hdb_df['town'] == town) &
        (hdb_df[flat_col] == 1)
    ]

    if not filtered.empty:
        match = filtered.iloc[0]
        lat, lon = match['latitude'], match['longitude']
        block = str(match['block']).strip()
        street = match['street_name'].strip().title()
        popup = f"{block} {street}, {town.title()}"
        return html.Div(f"You selected: {popup} on {floor_level} floor."), [lat, lon], popup

    return html.Div("No matching HDBs found."), [1.3521, 103.8198], "No match found"
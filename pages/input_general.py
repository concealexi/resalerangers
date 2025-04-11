import dash
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

# Common styling

common_input_style = {
    'width': '100%',
    'fontSize': '16px',
    'marginBottom': '20px',
    'fontFamily': 'Inter, sans-serif',
    'padding': '10px',
    'border': '1px solid #ccc',
    'borderRadius': '4px',
    'boxSizing': 'border-box',
    'backgroundColor': 'white'
}

common_dropdown_style = {
    'width': '100%',
    'fontSize': '16px',
    'marginBottom': '20px'
}

register_page(__name__, path="/input-general")

layout = html.Div(children =[
    dcc.Location(id='url', refresh=True),
    html.Div(
            children=[
                dcc.Link("< back to start", href="/", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'color': 'black',
                    'textDecoration': 'none'
                })
            ],
            style={'marginLeft': '20px', 'marginTop': '20px'}
        ),

    html.H1("What property are you looking for?",
            style={
                'textAlign': 'center',
                'fontFamily': 'Inter, sans-serif',
                'fontWeight': 'bold',
                'fontSize': '2rem',
                'marginTop': '10px',
                'color': 'black'
            }
        ),
    html.P(
            "Please fill in the characteristics for the flat of your choice",
            style={
                'textAlign': 'center',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '1rem',
                'marginBottom': '30px',
                'color': 'black'
            }
        ),

    html.Div([
        html.Label("Town", style={
            'fontFamily': 'Inter, sans-serif',
            'fontWeight': 'bold',
            'marginBottom': '8px',
            'display': 'block',
            'textAlign': 'left'
        }),

        html.Div([
            dcc.Dropdown(
                id='newbie-town-dropdown',
                options=[{'label': town.title(), 'value': town} for town in towns],
                placeholder="Enter first town",
                style={'width': '100%'}
            ),
            dcc.Dropdown(
                id='newbie-town-dropdown_2',
                options=[{'label': town.title(), 'value': town} for town in towns],
                placeholder="Enter second town",
                style={'width': '100%'}
            )
        ], style={
            'display': 'flex',
            'gap': '20px',
            'justifyContent': 'space-between',
            'marginBottom': '10px'
        }),

        html.P("Please select 2 towns to continue!", style={
            'fontSize': '13px',
            'color': '#777',
            'fontFamily': 'Inter, sans-serif',
            'textAlign': 'center',
            'marginBottom': '20px'
        }),

        html.Label("Flat Type", style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'}),
        dcc.Dropdown(
            id='newbie-flat-type',
            options=[],
            placeholder='Enter flat type',
            style=common_dropdown_style
        ),

        html.Label("Floor Level", style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'}),
        dcc.Dropdown(
            id='newbie-floor-level',
            options=[
                {'label': 'Low', 'value': 'Low'},
                {'label': 'Medium', 'value': 'Medium'},
                {'label': 'High', 'value': 'High'}
            ],
            placeholder='Enter floor level',
            style=common_dropdown_style
        ),

        html.H4("You may also add additional filters for your search!", style={
            'fontFamily': 'Inter, sans-serif', 'marginBottom': '30px'
        }),
        html.Div([
                html.Label('Minimum Remaining Lease (Year)', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'}),
                html.Div('0-99', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'})
                    ], style={'display':'flex','justifyContent':'space-between','marginBottom':'10px'}),
        dcc.Slider(
            id='newbie-lease',
            min=0,
            max=99,
            step=1,
            tooltip={'placement':'bottom'}, className='my-slider',
            marks={0: '0', 99: '99 years'},
        ),
        html.P("Select how long the minimum remaining lease you want your unit to be", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Inter, sans-serif',
            'marginBottom': '30px'
        }),
        html.Div([
                html.Label('Distance to nearest MRT (km)', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'}),
                html.Div('0-2.5', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'})
                    ], style={'display':'flex','justifyContent':'space-between','marginBottom':'10px'}),
        dcc.Slider(
            id='newbie-dist-mrt',
            min=0,
            max=2.5,
            step=0.1,
            tooltip={'placement':'bottom'}, className='my-slider',
            marks={0: '0', 2.5: '2.5km'},
        ),
        html.P("Select a maximum distance from the nearest available MRT", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Inter, sans-serif',
            'marginBottom': '30px'
        }),

        html.Div([
                html.Label('Distance to nearest Primary School (km)', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'}),
                html.Div('0-2.5', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'})
                    ], style={'display':'flex','justifyContent':'space-between','marginBottom':'10px'}),

        dcc.Slider(
            id='newbie-dist-school',
            min=0,
            max=2.5,
            step=0.1,
            tooltip={'placement':'bottom'}, className='my-slider',
            marks={0: '0', 2.5: '2.5km'},
        ),
        html.P("Select a maximum distance from the nearest available school", style={
            'fontSize': '13px', 'color': '#777', 'fontFamily': 'Inter, sans-serif',
            'marginBottom': '30px'
        }),

        html.Div([
            html.Button("See Units Now", id="newbie-submit", n_clicks=0, style={
                    'padding': '10px 20px',
                    'fontSize': '16px',
                    'cursor': 'pointer',
                    'backgroundColor': '#7F0019',
                    'color': 'white',
                    'fontFamily': 'Inter, sans-serif',
                    'border': 'none',
                    'borderRadius': '8px'
                })
        ], style={"textAlign": "center", "marginTop": "20px"}),

        html.Div(id='newbie-output', style={'marginTop': '30px', 'fontFamily': 'Inter, sans-serif'})
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '40px', 'fontFamily': 'Inter, sans-serif'})
],
    style={
        'backgroundColor': 'white',
        'minHeight': '100vh',
        'padding': '40px'
    })

# CALLBACKS

@callback(
    Output('newbie-flat-type', 'options'),
    Input('newbie-town-dropdown', 'value'),
    Input('newbie-town-dropdown_2', 'value')
)
def update_flat_type_options(town1, town2):
    if not town1 or not town2:
        return []

    filtered1 = hdb_df[hdb_df['town'] == town1]
    filtered2 = hdb_df[hdb_df['town'] == town2]

    flat_type_cols = [
        'flat_type_1 ROOM', 'flat_type_2 ROOM', 'flat_type_3 ROOM',
        'flat_type_4 ROOM', 'flat_type_5 ROOM',
        'flat_type_EXECUTIVE', 'flat_type_MULTI-GENERATION'
    ]

    counts1 = filtered1[flat_type_cols].sum()
    counts2 = filtered2[flat_type_cols].sum()

    # Only keep flat types that exist in both towns
    common_cols = counts1[(counts1 > 0) & (counts2 > 0)].index.tolist()

    return [
        {'label': col.replace('flat_type_', '').replace('_', ' ').title(), 'value': col.replace('flat_type_', '')}
        for col in common_cols
    ]



@callback(
    Output('user-filter-store', 'data'),
    Output('url', 'pathname'),
    Input('newbie-submit', 'n_clicks'),
    State('newbie-town-dropdown', 'value'),
    State('newbie-town-dropdown_2', 'value'),
    State('newbie-flat-type', 'value'),
    State('newbie-floor-level', 'value'),
    State('newbie-lease', 'value'),
    State('newbie-dist-mrt', 'value'),
    State('newbie-dist-school', 'value'),
    prevent_initial_call=True
)
def save_inputs_and_go(n_clicks, town1, town2, flat_type, floor_level, lease, dist_mrt, dist_school):

    if not town1 or not town2 or not flat_type or not floor_level:
        return dash.no_update, dash.no_update

    filter_data = {
        'town1': town1,
        'town2': town2,
        'flat_type': flat_type,
        'floor_level': floor_level
    }

    if lease is not None:
        filter_data['remaining_lease'] = lease
    if dist_mrt is not None:
        filter_data['max_dist_mrt'] = dist_mrt
    if dist_school is not None:
        filter_data['max_dist_school'] = dist_school

    return filter_data, "/output-general"
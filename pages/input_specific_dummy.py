from dash import html, dcc, register_page, callback, Output, Input, State, no_update
from functions.input_for_model import get_information
from functions.final_scraper import scraper_guru
from functions.percentile_floor import get_floor_est
import pandas as pd

register_page(__name__, path="/input-specific-dummy")

hdb_info = pd.read_csv("dataset/hdb_informations.csv")



# Define common styles for inputs
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

layout = html.Div(
    children=[
        # -- Top bar with "back to start" link --
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

        # -- Page Title --
        html.H1(
            "What property are you looking for?",
            style={
                'textAlign': 'center',
                'fontFamily': 'Inter, sans-serif',
                'fontWeight': 'bold',
                'fontSize': '2rem',
                'marginTop': '10px',
                'color': 'black'
            }
        ),

        # -- Subheading --
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

        # Hidden location component for redirection
        dcc.Location(id='redirect-location-dummy', refresh=True),

        # -- Custom Toggle (Segmented Control) using manual inputs/labels --
        html.Div(
            dcc.RadioItems(
                id='input-mode',
                options=[
                    {'label':'Manual Input',            'value':'manual'},
                    {'label':'Input from PropertyGuru', 'value':'guru'}
                ],
                value='manual',
                inline=True,
                className='mode-toggle-container',
                labelClassName='mode-toggle-label',
                inputClassName='mode-toggle-input'
            ),
            style={'display':'flex','justifyContent':'center','marginBottom':'30px'}
        ),

        # -- Main Form Container --
        html.Div(
            id='manual-input-container',
            style={'display':'block','width':'600px','margin':'0 auto','textAlign':'left'},
            children=[
                # Postal Code
                html.Label('Postal Code', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Input(id='expert-postal-code', type='number', placeholder='Enter postal code',
                          className='no-spinner',
                          style=common_input_style),

                # Flat Type
                html.Label('Flat Type', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Dropdown(id='expert-flat-type', options=[
                    {'label':'1 Room','value':'1 ROOM'},
                    {'label':'2 Room','value':'2 ROOM'},
                    {'label':'3 Room','value':'3 ROOM'},
                    {'label':'4 Room','value':'4 ROOM'},
                    {'label':'5 Room','value':'5 ROOM'},
                    {'label':'Executive','value':'EXECUTIVE'},
                    {'label':'Multi-Generation','value':'MULTI-GENERATION'}
                ], placeholder='Select Flat Type', className='my-dropdown', style=common_dropdown_style),

                # Square Area
                html.Div([
                    html.Div([
                        html.Label('Square Area (sqm)', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'}),
                        html.Div('0–250', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'})
                    ], style={'display':'flex','justifyContent':'space-between','marginBottom':'10px'}),
                    dcc.Slider(id='expert-square-area', min=0, max=250, value=0, step=1,
                               tooltip={'placement':'bottom'}, className='my-slider')
                ], style={'marginBottom':'30px'}),

                # Floor Level (Manual)
                html.Label('Floor Level', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Input(id='expert-floor-level-manual', type='number',
                          placeholder='Enter floor level', className='no-spinner', style=common_input_style),
                
                # Remaining Lease
                html.Label('Remaining Lease (years)', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Input(id='expert-remaining-lease', type='number',
                          placeholder='Enter remaining lease years', className='no-spinner', style=common_input_style),
            ]
        ),

        # ----- PropertyGuru Input Container -----
        html.Div(
            id='guru-input-container',
            style={'display':'none','width':'600px','margin':'0 auto','textAlign':'left'},
            children=[
                html.Label('PropertyGuru Link', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Input(id='expert-propertyguru-url', type='text',
                          placeholder='Enter valid URL', style=common_input_style),

                html.Label('Floor Level', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Dropdown(id='expert-floor-level-guru', options=[
                    {'label':'Ground floor','value':'Ground'},
                    {'label':'Low','value':'Low'},
                    {'label':'Mid','value':'Mid'},
                    {'label':'High','value':'High'},
                    {'label': 'Penthouse','value':'Penthouse'}
                ], placeholder='Select Floor Level', className='my-dropdown', style=common_dropdown_style),
            ]
        ),

        # Center the Submit button
        html.Div(
            html.Button(
                'Calculate Price',
                id='submit-expert-input',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'fontSize': '16px',
                    'cursor': 'pointer',
                    'backgroundColor': '#7F0019',
                    'color': 'white',
                    'fontFamily': 'Inter, sans-serif',
                    'border': 'none',
                    'borderRadius': '8px'
                }
            ),
            style={"textAlign": "center", "marginTop": "20px"}
        ),

        # -- Error / Info Output --
        html.Div(
            id='expert-output-dummy',
            style={
                'marginTop': '30px',
                'fontFamily': 'Inter, sans-serif',
                'textAlign': 'center'
            }
        )
    ],
    style={
        'backgroundColor': 'white',
        'minHeight': '100vh',
        'padding': '40px'
    }
)

# -- Callback to Toggle Input Containers --
@callback(
    [Output('manual-input-container','style'),
     Output('guru-input-container','style')],
    Input('input-mode','value')
)
def toggle_input_containers(mode):
    manual_style = {'display':'block','width':'600px','margin':'0 auto','textAlign':'left'}
    guru_style   = {'display':'none', 'width':'600px','margin':'0 auto','textAlign':'left'}
    if mode=='manual':
        return manual_style, guru_style
    else:
        return guru_style, manual_style

# -- Callback to Validate & Redirect --
@callback(
    [Output('redirect-location-dummy','pathname'),
     Output('expert-output-dummy','children'),
     Output('manual-store', 'data'),
     Output('guru-store', 'data')],
    Input('submit-expert-input','n_clicks'),
    State('input-mode','value'),
    State('expert-postal-code','value'),
    State('expert-flat-type','value'),
    State('expert-square-area','value'),
    State('expert-floor-level-manual','value'),
    State('expert-remaining-lease','value'),
    State('expert-propertyguru-url','value'),
    State('expert-floor-level-guru','value')
)
def capture_expert_input(n, mode, postal, flat, area, floor_m, lease, url, floor_g):
    if n and n > 0:
        if mode == 'manual':
            if not all([postal, flat, area, floor_m, lease]):
                return no_update, "Please fill in all fields for manual input.", no_update, no_update
            try:
                # Get model-ready input vector
                formatted_input = get_information(postal, flat, area, floor_m, lease)

                # Get street_name from hdb_info
                postal = str(postal)
                address_row = hdb_info[hdb_info['postal_code'].astype(str) == postal]
                if address_row.empty:
                    return no_update, f"No address found for postal code {postal}", no_update, no_update

                street_name = address_row.iloc[0]['address']
                full_address = f"{street_name}, Singapore {postal}"

                manual_data = {
                    "input_vector": formatted_input,
                    "flat_type_input": flat.replace('_', ' ').title(),
                    "address": full_address
                }

                return '/page-4', None, manual_data, {}

            except Exception as e:
                return no_update, f"Error formatting inputs: {e}", no_update, no_update

        else:
            if not all([url, floor_g]):
                return no_update, "Please provide the PropertyGuru link and Floor Level.", no_update, no_update
            guru_scrape = scraper_guru(url)
            postal_code = guru_scrape['postal_code']
            flat_type = guru_scrape['flat_type_label']
            sqm = int(guru_scrape['floor_area_sqm'])
            try:
                remaining_lease = int(guru_scrape['remaining_lease_year'])
            except (ValueError, TypeError, KeyError):
                lease_start = hdb_info[hdb_info['postal_code'].astype(str) == str(postal_code)]['year_completed']
                if lease_start.empty:
                    raise ValueError(f"Could not find lease start year for postal code {postal_code}")
                lease_start_year = int(lease_start.iloc[0])
                remaining_lease = 99 - (2025 - lease_start_year)
            max_floor = hdb_info[hdb_info['postal_code'].astype(str) == postal_code]['max_floor_lvl'].iloc[0]
            floor_est = get_floor_est(max_floor, floor_g)
            formatted_input = get_information(int(postal_code), flat_type, sqm, floor_est, remaining_lease)
            address = str(guru_scrape['address'])
            full_address = f"{address}, Singapore {postal_code}"
            guru_data = {
                "input_vector": formatted_input,
                "flat_type_input": flat_type.replace('_', ' ').title(),
                "address": full_address
            }
            return '/page-4', None, {}, guru_data
    return no_update, None, no_update, no_update

@callback(
    Output('expert-flat-type', 'options'),
    Input('expert-postal-code', 'value')
)
def update_flat_type_options(postal_code):
    if not postal_code:
        return []

    # Ensure postal code is string for matching
    filtered = hdb_info[hdb_info['postal_code'].astype(str) == str(postal_code)]

    if filtered.empty:
        return []

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


from dash import html, dcc, register_page, callback, Output, Input, State, no_update

register_page(__name__, path="/input-specific-dummy")

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
                        html.Div('0–500', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold'})
                    ], style={'display':'flex','justifyContent':'space-between','marginBottom':'10px'}),
                    dcc.Slider(id='expert-square-area', min=0, max=500, value=250, step=1,
                               tooltip={'placement':'bottom'}, className='my-slider')
                ], style={'marginBottom':'30px'}),

                # Floor Level (Manual)
                html.Label('Floor Level', style={'fontFamily': 'Inter, sans-serif', 'fontWeight':'bold','marginBottom':'5px'}),
                dcc.Dropdown(id='expert-floor-level-manual', options=[
                    {'label':'Low (1-3)','value':'Low'},
                    {'label':'Mid (4-9)','value':'Mid'},
                    {'label':'High (10+)','value':'High'}
                ], placeholder='Select Floor Level', className='my-dropdown', style=common_dropdown_style),

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
                    {'label':'Low (1-3)','value':'Low'},
                    {'label':'Mid (4-9)','value':'Mid'},
                    {'label':'High (10+)','value':'High'}
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
     Output('expert-output-dummy','children')],
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
    if n and n>0:
        if mode=='manual':
            if not all([postal, flat, area, floor_m, lease]):
                return no_update, "Please fill in all fields for manual input."
            return '/page-4', None
        else:
            if not all([url, floor_g]):
                return no_update, "Please provide the PropertyGuru link and Floor Level."
            return '/page-4', None
    return no_update, None
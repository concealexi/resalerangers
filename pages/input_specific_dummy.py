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

# For dropdowns, we remove our own border settings so that our custom CSS can take over
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

        # -- Main Form Container --
        html.Div(
            children=[
                # Postal Code
                html.Label("Postal Code", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontWeight': 'bold',
                    'display': 'block',
                    'marginBottom': '5px'
                }),
                dcc.Input(
                    id='expert-postal-code',
                    type='number',
                    placeholder='Enter postal code',
                    className='no-spinner',
                    style=common_input_style
                ),

                # Flat Type – add a custom class to target in CSS
                html.Label("Flat Type", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontWeight': 'bold',
                    'display': 'block',
                    'marginBottom': '5px'
                }),
                dcc.Dropdown(
                    id='expert-flat-type',
                    options=[
                        {'label': '1 Room', 'value': '1 ROOM'},
                        {'label': '2 Room', 'value': '2 ROOM'},
                        {'label': '3 Room', 'value': '3 ROOM'},
                        {'label': '4 Room', 'value': '4 ROOM'},
                        {'label': '5 Room', 'value': '5 ROOM'},
                        {'label': 'Executive', 'value': 'EXECUTIVE'},
                        {'label': 'Multi-Generation', 'value': 'MULTI-GENERATION'}
                    ],
                    placeholder='Select Flat Type',
                    className="my-dropdown",
                    style=common_dropdown_style
                ),

                # Square Area
                html.Label("Square Area (0–500)", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontWeight': 'bold',
                    'display': 'block',
                    'marginBottom': '5px'
                }),
                html.Div(
                    dcc.Slider(
                        id='expert-square-area',
                        min=0,
                        max=500,
                        step=1,
                        value=250,
                        marks={0: '0', 500: '500'},
                        tooltip={'placement': 'bottom'}
                    ),
                    style={'marginBottom': '30px'}
                ),

                # Floor Level – add same custom class
                html.Label("Floor Level", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontWeight': 'bold',
                    'display': 'block',
                    'marginBottom': '5px'
                }),
                dcc.Dropdown(
                    id='expert-floor-level',
                    options=[
                        {'label': 'Low (1-3)', 'value': 'Low'},
                        {'label': 'Mid (4-9)', 'value': 'Mid'},
                        {'label': 'High (10+)', 'value': 'High'}
                    ],
                    placeholder='Select Floor Level',
                    className="my-dropdown",
                    style=common_dropdown_style
                ),

                # Remaining Lease
                html.Label("Remaining Lease (years)", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontWeight': 'bold',
                    'display': 'block',
                    'marginBottom': '5px'
                }),
                dcc.Input(
                    id='expert-remaining-lease',
                    type='number',
                    placeholder='Enter remaining lease years',
                    className='no-spinner',
                    style=common_input_style
                ),

                # Separator text
                html.Div(
                    "Or simply enter the url of a listing on PropertyGuru, and we'll do the rest!",
                    style={
                        'fontFamily': 'Inter, sans-serif',
                        'fontWeight': 'bold',
                        'marginBottom': '5px',
                        'marginTop': '10px'
                    }
                ),

                # URL input
                html.Label("Paste your link here!", style={
                    'fontFamily': 'Inter, sans-serif',
                    'fontWeight': 'bold',
                    'display': 'block',
                    'marginBottom': '5px'
                }),
                dcc.Input(
                    id='expert-propertyguru-url',
                    type='text',
                    placeholder='Enter valid URL',
                    style=common_input_style
                ),

                # Submit Button
                html.Button(
                    'Submit',
                    id='submit-expert-input',
                    n_clicks=0,
                    style={
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'cursor': 'pointer',
                        'backgroundColor': 'black',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '8px',
                        'marginTop': '10px'
                    }
                ),

                # Error / Info output
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
                'width': '600px',
                'margin': '0 auto',
                'textAlign': 'left'
            }
        )
    ],
    style={
        'backgroundColor': 'white',
        'minHeight': '100vh',
        'padding': '40px'
    }
)

@callback(
    [Output('redirect-location-dummy', 'pathname'),
     Output('expert-output-dummy', 'children')],
    Input('submit-expert-input', 'n_clicks'),
    State('expert-postal-code', 'value'),
    State('expert-flat-type', 'value'),
    State('expert-square-area', 'value'),
    State('expert-floor-level', 'value'),
    State('expert-remaining-lease', 'value'),
    State('expert-propertyguru-url', 'value')
)
def capture_expert_input(n_clicks, postal_code, flat_type, square_area, floor_level, remaining_lease, propertyguru_url):
    if n_clicks > 0:
        if not any([postal_code, flat_type, floor_level, remaining_lease, propertyguru_url]):
            return no_update, html.Div("Please fill in at least one field or provide a URL.", style={'color': 'red'})
        return "/page-4", None
    return no_update, None

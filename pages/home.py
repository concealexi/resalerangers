import dash
from dash import html, dcc, register_page

register_page(__name__, path="/")

card_style = {
    'width': '400px',
    'height': '330px',
    'border': '6px solid #7F0019',
    'borderRadius': '20px',
    'padding': '20px',
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'textAlign': 'center',
    'backgroundColor': '#fff'
}

top_section = html.Div([
    html.H1(
        "HDB Resale Radar",
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'fontWeight': 'bold',
            'fontSize': '2.2rem',
            'margin': '20px 0 5px 0',
            'color': 'black'
        }
    ),
    html.P(
        "Your Guide to Smarter HDB Decisions",
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'margin': '0 0 20px 0',
            'color': 'black',
            'fontWeight': 'bold'
        }
    ),
    html.Div(
        style={
            'width': '80%',
            'margin': '0 auto 20px auto',
            'borderBottom': '3px solid #7F0019',
            'position': 'relative'
        },
        children=[
            # Left circle
            html.Div(
                style={
                    'width': '15px',
                    'height': '15px',
                    'backgroundColor': '#7F0019',
                    'borderRadius': '50%',
                    'position': 'absolute',
                    'left': '-7.5px',
                    'top': '-6px'
                }
            ),
            # Right circle
            html.Div(
                style={
                    'width': '15px',
                    'height': '15px',
                    'backgroundColor': '#7F0019',
                    'borderRadius': '50%',
                    'position': 'absolute',
                    'right': '-7.5px',
                    'top': '-6px'
                }
            )
        ]
    )
])

layout = html.Div([
    # Top section
    top_section,

    # Prompt text split into two elements
    html.Div(
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'fontWeight': 'bold',
            'color': 'black',
            'marginBottom': '40px'
        },
        children=[
            html.Div(
                "What brings you here today?",
                style={'fontSize': '1.8rem'}  # increased size for the first text
            ),
            html.Div(
                "This lets us better address your needs",
                style={'fontSize': '1.1rem'}  # keep as is
            )
        ]
    ),

    # Cards container
    html.Div(
        children=[
            # Left Card
            dcc.Link(
                html.Div([
                    # Icon container
                    html.Div(
                        html.Img(
                            src='assets/location_marker.svg',
                            style={'width': '90px', 'marginBottom': '10px'}
                        ),
                        style={
                            'width': '100%',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'marginTop': '20px'
                        }
                    ),
                    html.Div(style={'flexGrow': 1}),  # Spacer
                    html.Div([
                        html.H2("I have Specific Ideas",
                                style={
                                    'fontFamily': 'Inter, sans-serif',
                                    'color': 'black',
                                    'height': '110px',
                                    'marginBottom': '-50px'
                                }),
                        html.P(
                            [
                                "Get a tailored price prediction for",
                                html.Br(),
                                "your ideal flat."
                            ],
                            style={
                                'fontFamily': 'Inter, sans-serif',
                                'color': 'black',
                                'height': '100px'
                            }
                        )
                    ], style={'marginBottom': '20px'})
                ], style=card_style),
                href='/input-specific-dummy',
                style={'textDecoration': 'none'}
            ),

            # Right Card
            dcc.Link(
                html.Div([
                    # Icon container
                    html.Div(
                        html.Img(
                            src='assets/map.svg',
                            style={'width': '90px', 'marginBottom': '10px'}
                        ),
                        style={
                            'width': '100%',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'marginTop': '20px'
                        }
                    ),
                    html.Div(style={'flexGrow': 1}),  # Spacer
                    html.Div([
                        html.H2("I am Exploring Options",
                                style={
                                    'fontFamily': 'Inter, sans-serif',
                                    'color': 'black',
                                    'height': '110px',
                                    'marginBottom': '-50px'
                                }),
                        html.P(
                            [
                                "Explore market insights, price",
                                html.Br(),
                                "ranges and town comparisons."
                            ],
                            style={
                                'fontFamily': 'Inter, sans-serif',
                                'color': 'black',
                                'height': '100px'
                            }
                        )
                    ], style={'marginBottom': '20px'})
                ], style=card_style),
                href='/input-general',
                style={'textDecoration': 'none'}
            )
        ],
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'gap': '150px',
            'flexWrap': 'wrap',
            'margin': '0 auto'
        }
    ),

    # Row containing "We provide" (left) and ticks
    html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'flex-start',
            'width': '80%',
            'margin': '40px auto 0 auto'
        },
        children=[
            # Left column: "We provide" header and ticks list
            html.Div(
                children=[
                    html.H3("We provide:",
                            style={
                                'fontFamily': 'Inter, sans-serif',
                                'color': 'black',
                                'textAlign': 'left',
                                'marginBottom': '20px'
                            }),
                    # Ticks list with indent, italic, and enlarged text
                    html.Div([
                        html.Div([
                            html.Img(src='assets/tick.svg',
                                     style={'width': '24px', 'marginRight': '10px'}),
                            html.Span(
                                "Instant Price Predictions",
                                style={
                                    'fontFamily': 'Inter, sans-serif',
                                    'color': 'black',
                                    'fontSize': '1.5rem',
                                    'fontWeight': 'bold',
                                    'fontStyle': 'italic'
                                }
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px', 'marginLeft': '20px'}),

                        html.Div([
                            html.Img(src='assets/tick.svg',
                                     style={'width': '24px', 'marginRight': '10px'}),
                            html.Span(
                                "Past Transaction Insights (2015-2024)",
                                style={
                                    'fontFamily': 'Inter, sans-serif',
                                    'color': 'black',
                                    'fontSize': '1.5rem',
                                    'fontWeight': 'bold',
                                    'fontStyle': 'italic'
                                }
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px', 'marginLeft': '20px'}),

                        html.Div([
                            html.Img(src='assets/tick.svg',
                                     style={'width': '24px', 'marginRight': '10px'}),
                            html.Span(
                                "Town-by-Town Market Trends",
                                style={
                                    'fontFamily': 'Inter, sans-serif',
                                    'color': 'black',
                                    'fontSize': '1.5rem',
                                    'fontWeight': 'bold',
                                    'fontStyle': 'italic'
                                }
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px', 'marginLeft': '20px'})
                    ], style={'textAlign': 'left'})
                ],
                style={'width': '60%'}
            )
        ]
    ),

    # Footer section with reduced gap at the bottom
    html.Div(
        "Resale Rangers aim at safeguarding you with transparency in Singapore's resale market through data-driven insights.",
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'color': 'black',
            'marginTop': '30px',
            'fontSize': '0.9rem'
        }
    )
],
style={
    'margin': '0',
    'padding': '0',
    'minHeight': '100vh',
    'backgroundColor': '#FFFFFF',
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'flex-start'
})

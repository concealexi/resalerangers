import dash
from dash import html, dcc, Input, Output, callback, register_page
import joblib
import xgboost as xgb
from models.model_tuning import conformal_predict

# Register page 4 for proper routing
register_page(__name__, path="/page-4")

# Load the saved model package
model_package = joblib.load("models/final_model.pkl")
model = model_package['model']
q_value = model_package['q_value']

# Default input vector (in case stored data is not available)
default_input = [70, 0.415218792367851, 8.0, 1.0811219644208, 60, 9.76408651954306, 0, 0, 1, 0, 0, 0, 0]

layout = html.Div([
    html.H2("Fair Price Prediction"),
    html.P("This page was reached via redirect from the input page."),
    html.Button("Predict", id="predict-button", n_clicks=0, style={"margin-top": "20px"}),
    html.Div(id="prediction-output", style={"margin-top": "20px", "font-weight": "bold"})
])

@callback(
    Output("prediction-output", "children"),
    Input("predict-button", "n_clicks"),
    # We grab the stored manual data here:
    Input('manual-store', 'data')
)
def predict_fair_price(n_clicks, manual_data):
    if n_clicks:
        try:
            # If manual data is available, use that as the input vector;
            # otherwise, fallback to default_input.
            if manual_data and isinstance(manual_data, list) and len(manual_data) > 0:
                input_vector = manual_data[0]  # If get_information returns a list with one row
            else:
                input_vector = default_input
            # Call your conformal_predict function
            y_pred, y_lower, y_upper = conformal_predict(model, input_vector, q_value)
            return html.Div([
                html.P(f"Predicted Price: {y_pred[0]:.2f}"),
                html.P(f"90% Confidence Interval: [{y_lower[0]:.2f}, {y_upper[0]:.2f}]")
            ])
        except Exception as e:
            return f"Error in prediction: {e}"
    return ""

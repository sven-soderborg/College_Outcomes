import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px


# Load the data from the CSV file
data = pd.read_csv("Data/clean_field_of_study.csv")


def get_sorted_data(df, sort_by_instnm=True, sort_by_cipdef=True):
    """
    Sorts the data based on the given criteria.
    """
    sort_columns = []
    if sort_by_instnm:
        sort_columns.append("INSTNM")
    if sort_by_cipdef:
        sort_columns.append("CIPDEF")

    return df.sort_values(by=sort_columns)


def get_average_earnings(df):
    """
    Computes the average earnings for 1 and 4 years after graduation.
    """
    avg_earn_1yr = df["EARN_MDN_1YR"].mean()
    avg_earn_4yr = df["EARN_MDN_4YR"].mean()

    return avg_earn_1yr, avg_earn_4yr


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    [
        # Dropdown for sorting options
        html.Div(
            [
                html.Label("Sort by Institution Name:"),
                dcc.Dropdown(
                    id="instnm-dropdown",
                    options=[
                        {"label": "Yes", "value": "yes"},
                        {"label": "No", "value": "no"},
                    ],
                    value="yes",
                    clearable=False,
                ),
                html.Label("Sort by CIP Definition:"),
                dcc.Dropdown(
                    id="cipdef-dropdown",
                    options=[
                        {"label": "Yes", "value": "yes"},
                        {"label": "No", "value": "no"},
                    ],
                    value="yes",
                    clearable=False,
                ),
            ]
        ),
        # Button to apply sorting
        html.Button("Apply Sorting", id="sort-button"),
        # Placeholder for table and visuals
        html.Div(id="table-output"),
        html.Div(id="visual-output"),
    ]
)


@app.callback(
    Output("table-output", "children"),
    Input("sort-button", "n_clicks"),
    Input("instnm-dropdown", "value"),
    Input("cipdef-dropdown", "value"),
)
def update_table(n_clicks, instnm_value, cipdef_value):
    # Check if button is clicked
    if not n_clicks:
        return dash.no_update

    # Get the sorted data based on dropdown values
    sort_by_instnm = instnm_value == "yes"
    sort_by_cipdef = cipdef_value == "yes"
    sorted_data = get_sorted_data(data, sort_by_instnm, sort_by_cipdef)

    # Convert sorted data to a Dash DataTable and return
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in sorted_data.columns],
        data=sorted_data.to_dict("records"),
        page_size=10,  # Display only 10 rows per page
    )
    return table


@app.callback(
    Output("visual-output", "children"),
    Input("sort-button", "n_clicks"),
    Input("instnm-dropdown", "value"),
    Input("cipdef-dropdown", "value"),
)
def update_visuals(n_clicks, instnm_value, cipdef_value):
    # Check if button is clicked
    if not n_clicks:
        return dash.no_update

    # Get the sorted data based on dropdown values
    sort_by_instnm = instnm_value == "yes"
    sort_by_cipdef = cipdef_value == "yes"
    sorted_data = get_sorted_data(data, sort_by_instnm, sort_by_cipdef)

    # Compute the average earnings
    avg_earn_1yr, avg_earn_4yr = get_average_earnings(sorted_data)

    # Create a bar plot for the average earnings
    fig = px.bar(
        x=["1 Year After Graduation", "4 Years After Graduation"],
        y=[avg_earn_1yr, avg_earn_4yr],
        labels={"x": "Time", "y": "Average Earnings"},
        title="Average Earnings After Graduation",
    )

    # Return the figure
    return dcc.Graph(figure=fig)


if __name__ == "__main__":
    app.run_server(debug=True)

import plotly.express as px
import pandas as pd
import requests

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.FLATLY],
                requests_pathname_prefix='/election/',
                routes_pathname_prefix='/election/')

base_url = "http://localhost:8000/"

response = requests.get(base_url + 'candidates_list')
candidates_list = response.json()['response']

# all data
filtered_df_dict = requests.get(base_url + 'candidates_all')
json_all = filtered_df_dict.json()
filtered_df_all = pd.DataFrame(json_all)

# top_candidate_positive_raw
json_top_candidate_raw = requests.get(base_url + 'top_candidate_positive_raw').json()
res_top_candidate_positive_raw = json_top_candidate_raw['response']
plot_top_candidate_positive_raw = [{'candidate': candidate, 'score': score} for candidate, score in res_top_candidate_positive_raw.items()]

# top_candidate_positive_proportion
json_top_candidate_positive_proportion = requests.get(base_url + 'top_candidate_positive_proportion').json()
res_top_candidate_positive_proportion = json_top_candidate_positive_proportion['response']
plot_top_candidate_positive_proportion = [{'candidate': candidate, 'score': score} for candidate, score in res_top_candidate_positive_proportion.items()]

# Layout of the application
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Filtres", className="display-7"),
            html.Hr(),
            html.P("Sélectionner un candidat", className="lead"),
            dcc.Dropdown(
                id='pie-candidate-dropdown',
                options=[
                    {'label': 'All', 'value': 'All'},
                    * [{'label': candidate, 'value': candidate} for candidate in candidates_list]
                ],
                value='All',
                placeholder="Sélectionner un candidat"
            ),
            ], width=3, className="bg-light sidebar"),
        dbc.Col([

            html.Div([
                html.H1('Elections américaines au fil des articles du NYT'),
                html.Div([
                    html.H5("Dernier article"),
                    html.Div([
                        html.Div(id='live-update-text'),
                        dcc.Interval(
                            id='interval-component',
                            interval=5 * 1000,  # in milliseconds
                            n_intervals=0
                        )
                    ])]),
                dcc.Graph(id='pie-chart'),
                dcc.Graph(id='histogram'),
                dcc.Graph(
                    id='top_5_positive_raw',
                    figure={
                        'data': [
                            {'x': [d['candidate']], 'y': [d['score']], 'type': 'bar', 'name': d['candidate']} for d in
                            plot_top_candidate_positive_raw
                        ],
                        'layout': {
                            'title': "Top 5 des candidats avec le plus d'articles positifs",
                            'xaxis': {'title': 'Candidates'},
                            'yaxis': {'title': 'Votes'}
                        }
                    }
                ),

                dcc.Graph(
                    id='top_5_positive_rproportion',
                    figure={
                        'data': [
                            {'x': [d['candidate']], 'y': [d['score']], 'type': 'bar', 'name': d['candidate']} for d in
                            plot_top_candidate_positive_proportion
                        ],
                        'layout': {
                            'title': "Top 5 des candidats avec le plus d'articles positifs en proportion",
                            'xaxis': {'title': 'Candidates'},
                            'yaxis': {'title': 'Votes'}
                        }
                    }
                )
            ]),



        ], width=9)
    ])
], fluid=True)




@app.callback(
    [Output('pie-chart', 'figure'),
     Output('histogram', 'figure')],
    [Input('pie-candidate-dropdown', 'value')]
)
def update_charts(selected_candidate):
    if selected_candidate == 'All':
        filtered_df = filtered_df_all
    else:
        filtered_df_dict = requests.get(base_url + 'candidates/' + selected_candidate)
        json_candidate = filtered_df_dict.json()
        filtered_df = pd.DataFrame(json_candidate)
        # filtered_df = data[data['main_candidate'] == selected_candidate]

    pie_colors = px.colors.qualitative.Plotly

    pie_fig = px.pie(filtered_df, names='cleaned_polarity', title=f'Polarité par candidat : {selected_candidate}', color='cleaned_polarity', color_discrete_map={'positive':'lightgreen',
                                 'negative':'red',
                                 'neutral':'blue'})
    hist_fig = px.histogram(filtered_df,
                            x='year',
                            title=f'Nombre d\'articles par année d\'élection pour le candidat : {selected_candidate}',
                            color_discrete_sequence=pie_colors,
                            barmode='group')

    return pie_fig, hist_fig

@app.callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    # Fetch data from FastAPI endpoint
    response = requests.get('http://localhost:8000/last_published_article')
    if response.status_code ==200:
        data = response.json()['response']

        # Prepare data for display (example assuming data is list of dicts)
        if len(data['main_candidate']) == 1:
            data_display = [
                html.Span("Titre : "+  str(data['headline'])),
                html.Hr(),
                html.Span("\nPolarité pour " + data['main_candidate'][0] + " : " + str([x['prediction'] for x in data['polarity'] if x['entity']==data['main_candidate'][0]]))
            ]
        elif len(data['main_candidate']) == 2:
            data_display = [
                html.Span("Titre : "+  str(data['headline'])),
                html.Hr(),
                html.Span("\nPolarité pour " + data['main_candidate'][0] + " : " + str([x['prediction'] for x in data['polarity'] if x['entity']==data['main_candidate'][0]])),
                html.Hr(),
                html.Span("\nPolarité pour " + data['main_candidate'][1] + " : " + str([x['prediction'] for x in data['polarity'] if x['entity'] == data['main_candidate'][1]]))
            ]

        return data_display


if __name__ == '__main__':
    app.run_server(debug=True, port=8052)

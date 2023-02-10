from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


path = "/sunspots/data/monthly_sunspots.csv"

sunspots = pd.read_csv(path, sep=';', header=None)[[0, 2, 3]]
sunspots.columns = ['year', 'date', 'sunspot_avg']


def select_years(df, yr_col, min_yr, max_yr):
    new = df[(df[yr_col] >= min_yr) & (df[yr_col] <= max_yr)]
    return new


def moving_avg(ls, window_size):
    avgs = []
    for i in range(len(ls) - window_size + 1):
        avg = sum(ls[i: i + window_size]) / window_size
        avgs.append(avg)

    return avgs


def get_cycle(df, date_col, mod, new_col='cycle_pos'):
    cycle_df = df
    cycle_df[new_col] = cycle_df.apply(lambda r: r[date_col] % mod, axis=1)

    return cycle_df


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    dbc.Row([
        html.H2('ANALYSIS OF SUNSPOT NUMBERS', style={'margin': '0', 'color': 'white'}),
        html.P('data from: https://soho.nascom.nasa.gov/data/realtime-images.html, '
               'https://www.sidc.be/silso/datafiles', style={'color': 'darkgrey', 'float': 'left', 'margin': '0'}),
        html.A('Learn More', href='https://en.wikipedia.org/wiki/Sunspot', target='_blank',
               style={'float': 'right', 'color': 'lightblue', 'margin-right': '10px'})
    ], style={'height': '6vh', 'background-color': 'rgba(0,0,0,0.8)', 'border': '5px solid black'}),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='sunspot', style={'margin': '10px'}),
                dbc.Row([
                        html.P('set year range:', style={'text-indent': '18px', 'font-style': 'italic',
                                                         'float': 'left'}),
                        dcc.Input(id='yr_min', value=1900, type='number', min=1749, max=2022,
                                  style={'float': 'left', 'margin': '15px', 'width': '50px'}),
                        html.P('–', style={'float': 'left'}),
                        dcc.Input(id='yr_max', value=2023, type='number', min=1750, max=2023,
                                  style={'float': 'left', 'margin': '15px', 'width': '50px'})
                        ], style={'width': '600px', 'height': '60px'}),
                dcc.RangeSlider(id='yr_range', min=1749, max=2023, step=1,
                                value=[1900, 2023],
                                marks={i: {'label': str(i),
                                           'style': {'color': 'white'}} for i in range(1749, 2023, 13)}),
                dbc.Row([
                        html.P('set moving average window (years):',
                               style={'text-indent': '18px', 'font-style': 'italic', 'float': 'left'}),
                        dcc.Input(id='window_input', value=10, type='number', min=1, max=100,
                                  style={'float': 'left', 'margin': '15px', 'width': '40px'})
                        ], style={'width': '600px', 'height': '60px'}),
                dcc.Slider(id='window_size', min=1, max=100, step=2, value=10,
                           marks={i: {'label': str(i), 'style': {'color': 'white'}} for i in range(1, 100, 5)})
            ], style={}),
        ], style={'width': '50vw', 'height': '91vh', 'float': 'left', 'overflow': 'hidden', 'align': 'bottom',
                  'background-color': 'rgba(90, 90, 90, 1)', 'border': '3px solid grey'}),
        dbc.Col([
            html.Div([
                    dcc.Graph(id='cycles', style={'margin-top': '10px', 'margin-left': '20px', 'margin-left': '20px'}),
                    dbc.Row([
                        html.P('set cycle length (years):', style={'text-indent': '18px', 'font-style': 'italic',
                                                           'float': 'left'}),
                        dcc.Input(id='cycle_input', value=11, type='number', min=1, max=50,
                                  style={'float': 'left', 'margin': '15px', 'width': '30px'})
                    ], style={'width': '600px', 'height': '60px'}),
                    dbc.Row([
                        dcc.Slider(id='cycle_slider', min=1, max=50, step=0.1, value=11,
                                   marks={i: {'label': str(i), 'style': {'color': 'white'}}
                                          for i in range(1, 50, 5)})
                    ]),
                ], style={'width': '48vw', 'height': '50vh', 'float': 'left'}),
            html.Div([
                dbc.Row([
                    html.P('Click To View Different Imaging Filters:',
                           style={'text-indent': '15px', 'font-weight': 'bold', 'font-size': '16px', 'color': 'white'})
                ], style={'margin-top': '20px'}),
                dbc.Row([
                    html.Div(id='hmi_div', children=[
                        html.Img(src='https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg',
                                 style={'width': '16vw', 'float': 'left'}, id='hmi'),
                    ]),
                    html.Div(id='eit_div', children=[
                        html.Img(src='https://soho.nascom.nasa.gov/data/LATEST/current_eit_171.gif',
                                 style={'width': '16vw', 'float': 'left'}, id='eit'),
                    ]),
                    html.Div(id='lasco_div', children=[
                        html.Img(src='https://soho.nascom.nasa.gov/data/LATEST/current_c2.gif',
                                 style={'width': '16vw', 'float': 'left'}, id='lasco'),
                    ])
                ]),
                dbc.Row([
                    html.Div([html.P(children='SDO/HMI Continuum', id='hmi_txt')],
                             style={'width': '16vw', 'float': 'left', 'text-align': 'left', 'margin': '0',
                                    'text-indent': '15px'}),
                    html.Div([html.P(children='EIT 171', id='eit_txt')],
                             style={'width': '16vw', 'float': 'left', 'text-align': 'left', 'margin': '0',
                                    'text-indent': '15px'}),
                    html.Div([html.P(children='LASCO C2', id='lasco_txt')],
                             style={'width': '16vw', 'float': 'left', 'text-align': 'left', 'margin': '0',
                                    'text-indent': '15px'})
                ], style={'margin-top': '15px'})
            ], style={'width': '48vw', 'height': '40vh', 'overflow': 'hidden'}),
        ], style={'width': '48vw', 'height': '91vh', 'float': 'left', 'overflow': 'hidden',
                  'background-color': 'rgba(90, 90, 90, 1)', 'border': '3px solid grey'})
    ])
    ], style={'font-family': 'Trebuchet MS', 'color': 'rgba(250, 250, 250, 0.8)', 'font-size': '15px'})


@app.callback(
    Output('yr_range', 'value'),
    Input('yr_min', 'value'),
    Input('yr_max', 'value')
)
def get_year_input(low, high):
    if low is None or high is None or low not in range(1749, high) or high not in range(low, 2023):
        return [1900, 2023]

    return [low, high]


@app.callback(
    Output('window_size', 'value'),
    Input('window_input', 'value')
)
def get_window_input(val):
    if val is not None:
        return val

    return 10


@app.callback(
    Output('sunspot', 'figure'),
    Input('window_size', 'value'),
    Input('yr_range', 'value')
)
def smooth_plot(window, yr_range):
    df = select_years(sunspots, 'year', yr_range[0], yr_range[1])

    smooth_x = moving_avg(df['date'].to_list(), window)
    smooth_y = moving_avg(df['sunspot_avg'].to_list(), window)
    smooth = pd.DataFrame({'date': smooth_x, 'avg': smooth_y})

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['sunspot_avg'], mode='lines', line_color='lightsteelblue',
                             line_width=1, name='Monthly'))
    fig.add_trace(go.Scatter(x=smooth['date'], y=smooth['avg'], mode='lines', line_color='orange', name='Smoothed'))

    fig.update_layout(width=700, height=500,
                      title=f'International Sunspot Number: Monthly Mean and {window}-Month Smoothed Number',
                      title_font_size=15,
                      xaxis_title=f'Time (Years {yr_range[0]}-{yr_range[1]})', yaxis_title='Sunspot Number',
                      paper_bgcolor='rgba(100, 100, 100, 0.8)', title_font_color='white', xaxis_color='white',
                      yaxis_color='white', legend_font_color='white', legend={'bgcolor': 'rgba(0, 0, 0, 0)'},
                      margin=dict(l=80, r=80, t=100, b=80))

    return fig


@app.callback(
    Output('cycle_slider', 'value'),
    Input('cycle_input', 'value')
)
def get_cycle_input(val):
    if val is not None:
        return val

    return 11


@app.callback(
    Output('cycles', 'figure'),
    Input('cycle_slider', 'value')
)
def cycle(mod):
    cycles = get_cycle(sunspots, 'date', mod)
    fig = px.scatter(cycles, x='cycle_pos', y='sunspot_avg')
    fig.update_traces(marker={'size': 3, 'color': 'steelblue'})

    fig.update_layout(width=650, height=300, title=f'Sunspot Cycle: {mod}', xaxis_title='Years',
                      yaxis_title='# of Sunspots', paper_bgcolor='rgba(100, 100, 100, 0.8)', title_font_color='white',
                      xaxis_color='white', yaxis_color='white', legend_font_color='white',
                      legend={'bgcolor': 'rgba(0, 0, 0, 0)'}, margin=dict(l=80, r=80, t=100, b=80))

    return fig


@app.callback(
    Output('hmi', 'src'),
    Output('hmi_txt', 'children'),
    Input('hmi_div', 'n_clicks')
)
def update_hmi(clicks):
    if clicks is None or clicks % 2 == 0:
        src = 'https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg'
        txt = 'SDO/HMI Continuum'
    else:
        src = 'https://soho.nascom.nasa.gov/data/realtime/hmi_mag/1024/latest.jpg'
        txt = 'SDO/HMI Magnetogram'

    return src, txt


@app.callback(
    Output('eit', 'src'),
    Output('eit_txt', 'children'),
    Input('eit_div', 'n_clicks')
)
def update_eit(clicks):
    if clicks is None or clicks % 4 == 0:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_eit_171.gif'
        txt = 'EIT 171'
    elif clicks % 4 == 1:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_eit_195.gif'
        txt = 'EIT 195'
    elif clicks % 4 == 2:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_eit_284.gif'
        txt = 'EIT 284'
    else:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_eit_304.gif'
        txt = 'EIT 304'

    return src, txt


@app.callback(
    Output('lasco', 'src'),
    Output('lasco_txt', 'children'),
    Input('lasco_div', 'n_clicks')
)
def update_lasco(clicks):
    if clicks is None or clicks % 2 == 0:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_c2.gif'
        txt = 'LASCO C2'
    else:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_c3.gif'
        txt = 'LASCO C3'

    return src, txt


if __name__ == "__main__":
    app.run_server(debug=True)

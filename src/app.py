"""
Kate Lanman
DS3500
HW2
created 02/03/2023
updated on 02/10/2023
"""
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# create global df for sunspot data
sunspots = pd.read_csv('data/monthly_sunspots.csv', sep=';', header=None)[[0, 2, 3]]
sunspots.columns = ['year', 'date', 'sunspot_avg']


def select_years(df, yr_col, min_yr, max_yr):
    """
    Filters dataframe for select range of years.

    :param df: dataframe; dataframe to grab from
    :param yr_col: str; column containing year data
    :param min_yr: int; low end of range
    :param max_yr: int; high end of range
    :return: dataframe; filtered dataframe
    """
    new = df[(df[yr_col] >= min_yr) & (df[yr_col] <= max_yr)]
    return new


def moving_avg(ls, window_size):
    """
    Aggregates data into groups of specified size and calculates group averages to
    get a series of averages (moving average)

    :param ls: list of numbers; list to calculate moving average for
    :param window_size: int; size of window to calculate averages on
    :return: list; a list of averages (moving average)
    """
    avgs = []

    for i in range(len(ls) - window_size + 1):

        # get average for current group
        avg = sum(ls[i: i + window_size]) / window_size
        avgs.append(avg)

    return avgs


def get_cycle(df, date_col, cycle_length, new_col='cycle_pos'):
    """
    Create new dataframe containing column indicating which point in the cycle a datapoint was from

    :param df: dataframe
    :param date_col: str; column containing time data (number) to calculate cycle on
    :param cycle_length: number; cycle length
    :param new_col: str; optional new name for created column (default = 'cycle_pos')
    :return: dataframe; dataframe containing original data plus an additional column for cycle
    """
    cycle_df = df
    cycle_df[new_col] = cycle_df[date_col] % cycle_length

    return cycle_df


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    # site header
    dbc.Row([
        html.H2('ANALYSIS OF SUNSPOT NUMBERS', style={'margin': '0', 'color': 'white'}),
        html.P('data from: https://soho.nascom.nasa.gov/data/realtime-images.html (https://goo.gl/PXrLYd), '
               'https://www.sidc.be/silso/datafiles', style={'color': 'darkgrey', 'float': 'left', 'margin': '0'}),
        html.A('Learn More', href='https://en.wikipedia.org/wiki/Sunspot', target='_blank',
               style={'float': 'right', 'color': 'lightblue', 'margin-right': '10px'})
    ], style={'height': '6vh', 'background-color': 'rgba(0,0,0,0.8)', 'border': '5px solid black'}),

    # site body - sunspot data and images
    dbc.Row([
        dbc.Col([

            # div 1 - monthly sunspot analysis
            html.Div([
                dcc.Graph(id='sunspot', style={'width': '48vw', 'height': '60vh', 'margin': '10px'}),

                # graph controls - year range, moving average window
                dbc.Row([
                        html.P('set year range:', style={'text-indent': '18px', 'font-style': 'italic',
                                                         'float': 'left'}),
                        dcc.Input(id='yr_min', value=1900, type='number', min=1749, max=2022, step=1,
                                  style={'float': 'left', 'margin': '15px', 'width': '50px'}),
                        html.P('–', style={'float': 'left'}),
                        dcc.Input(id='yr_max', value=2023, type='number', min=1750, max=2023, step=1,
                                  style={'float': 'left', 'margin': '15px', 'width': '50px'})
                        ], style={'width': '600px', 'height': '60px'}),

                # only slider controls graph in current version
                dcc.RangeSlider(id='yr_range', min=1749, max=2023, step=1,
                                value=[1900, 2023],
                                marks={i: {'label': str(i),
                                           'style': {'color': 'white'}} for i in range(1749, 2023, 13)}),
                dbc.Row([
                        html.P('set moving average window (years):',
                               style={'text-indent': '18px', 'font-style': 'italic', 'float': 'left'}),
                        dcc.Input(id='window_input', value=10, type='number', min=1, max=100, step=1,
                                  style={'float': 'left', 'margin': '15px', 'width': '40px'})
                        ], style={'width': '600px', 'height': '60px'}),

                # only slider controls graph in current version
                dcc.Slider(id='window_size', min=1, max=100, step=2, value=10,
                           marks={i: {'label': str(i), 'style': {'color': 'white'}} for i in range(1, 100, 5)})
            ], style={}),
        ], style={'width': '50vw', 'height': '91vh', 'float': 'left', 'overflow': 'hidden', 'align': 'bottom',
                  'background-color': 'rgba(90, 90, 90, 1)', 'border': '3px solid grey'}),
        dbc.Col([

            # div 2 - sunspot cycle analysis
            html.Div([
                    dcc.Graph(id='cycles', style={'width': '45vw', 'height': '40vh', 'margin-top': '10px',
                                                  'margin-left': '20px', 'margin-left': '20px'}),

                    # graph controls - cycle length to a fraction of a year
                    dbc.Row([
                        html.P('set cycle length (years):', style={'text-indent': '18px', 'font-style': 'italic',
                                                           'float': 'left'}),
                        dcc.Input(id='cycle_input', value=11, type='number', min=1, max=50,
                                  style={'float': 'left', 'margin': '15px', 'width': '30px'})
                    ], style={'width': '600px', 'height': '60px'}),

                    # only slider controls graph in current version
                    dbc.Row([
                        dcc.Slider(id='cycle_slider', min=1, max=50, step=0.1, value=11,
                                   marks={i: {'label': str(i), 'style': {'color': 'white'}}
                                          for i in range(1, 50, 5)})
                    ]),
                ], style={'width': '48vw', 'height': '50vh', 'float': 'left'}),

            # div 3 - sun images/gifs + labels
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
    """
    For year range on monthly sunspot analysis - set slider value to input value

    :param low: int; low end of range
    :param high: int; high end of range
    :return: list of ints; [low end of range, high end of range]
    """
    # ignore invalid inputs
    if low is None or high is None or low not in range(1749, high) or high not in range(low, 2023):
        return [1900, 2023]

    return [low, high]


@app.callback(
    Output('window_size', 'value'),
    Input('window_input', 'value')
)
def get_window_input(val):
    """
    For moving average size on monthly sunspot analysis - set slider value to input value

    :param val: int; window size from input
    :return: int; window size for slider
    """
    # ignore empty input
    if val is None:
        return 10

    return val


@app.callback(
    Output('sunspot', 'figure'),
    Input('window_size', 'value'),
    Input('yr_range', 'value')
)
def smooth_plot(window, yr_range):
    """
    Create plot of monthly sunspot averages with overlaid moving average for smoothing

    :param window: int; window to calculate moving average on
    :param yr_range: list of ints; range of years to include data on
    :return: figure to plot
    """
    # get filtered data on year
    df = select_years(sunspots, 'year', yr_range[0], yr_range[1])

    # moving avgs for date vs. monthly sunspot avg
    smooth_x = moving_avg(df['date'].to_list(), window)
    smooth_y = moving_avg(df['sunspot_avg'].to_list(), window)

    # overlay sunspot average and smoothed data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['sunspot_avg'], mode='lines', line_color='lightsteelblue',
                             line_width=1, name='Monthly'))
    fig.add_trace(go.Scatter(x=smooth_x, y=smooth_y, mode='lines', line_color='orange', name='Smoothed'))

    fig.update_layout(title=f'International Sunspot Number: Monthly Mean and {window}-Month Smoothed Number',
                      title_font_size=15,
                      xaxis_title=f'Time (Years {yr_range[0]}-{yr_range[1]})', yaxis_title='Sunspot Number',
                      paper_bgcolor='rgba(100, 100, 100, 0.8)', title_font_color='white', xaxis_color='white',
                      yaxis_color='white', legend_font_color='white', legend={'bgcolor': 'rgba(0, 0, 0, 0)'})

    return fig


@app.callback(
    Output('cycle_slider', 'value'),
    Input('cycle_input', 'value')
)
def get_cycle_input(val):
    """
    For cycle length on sunspot cycle analysis - set slider value to input value

    :param val: number; cycle length
    :return: number; value to set slider to
    """
    # ignore empty input
    if val is None:
        return 11

    return val


@app.callback(
    Output('cycles', 'figure'),
    Input('cycle_slider', 'value')
)
def cycle(cycle_length):
    """
    Create scatter plot to visualize sunspot cycles

    :param cycle_length: cycle length to position data on
    :return: figure to plot
    """
    # get cycle position based on fractional year
    cycles = get_cycle(sunspots, 'date', cycle_length)

    fig = px.scatter(cycles, x='cycle_pos', y='sunspot_avg')
    fig.update_traces(marker={'size': 3, 'color': 'steelblue'})

    fig.update_layout(title=f'Sunspot Cycle: {cycle_length}', xaxis_title='Years',
                      yaxis_title='# of Sunspots', paper_bgcolor='rgba(100, 100, 100, 0.8)', title_font_color='white',
                      xaxis_color='white', yaxis_color='white', legend_font_color='white',
                      legend={'bgcolor': 'rgba(0, 0, 0, 0)'}, margin=dict(l=100, r=60, t=110, b=80))

    return fig


@app.callback(
    Output('hmi', 'src'),
    Output('hmi_txt', 'children'),
    Input('hmi_div', 'n_clicks')
)
def update_hmi(clicks):
    """
    Update displayed image if clicked. Alternates between two images

    :param clicks: int; number of clicks
    :return: new image and label to display
    """
    # start image and image to display every other click
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
    """
    Update displayed image if clicked. Alternates between four gifs

    :param clicks: int; number of clicks
    :return: new image and label to display
    """
    # start image and image to display every four clicks
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
    """
    Update displayed image if clicked. Alternates between 2 gifs

    :param clicks: int; number of clicks
    :return: new image and label to display
    """
    # start image and image to display every other click
    if clicks is None or clicks % 2 == 0:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_c2.gif'
        txt = 'LASCO C2'

    else:
        src = 'https://soho.nascom.nasa.gov/data/LATEST/current_c3.gif'
        txt = 'LASCO C3'

    return src, txt


if __name__ == "__main__":
    app.run_server(debug=True)

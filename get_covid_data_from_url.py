import requests
import pandas as pd
from datetime import datetime
import eventlet

# Get data
covid_case_url = r'https://docs.google.com/spreadsheets/d/1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo/export?format=xlsx'



def get_covid_data(covid_case_url, method_='url'):
    # Initiate eventlet to manage request timeout
    eventlet.monkey_patch()

    if method_ == 'url':
        try:
            with eventlet.timeout.Timeout(10):
                s = requests.get(covid_case_url).content
                BytesIO = pd.io.common.BytesIO  # Wrap in BytesIO to make it a file-like object
                s = BytesIO(s)
                filesource_caveat = ''
        except:
            s = r'Data/Public_COVID-19_Canada.xlsx'
            filesource_caveat = ' [cached]'
    else:
        s = r'Data/Public_COVID-19_Canada.xlsx'
        filesource_caveat = ' [cached]'

    # Update Date
    update_date = pd.read_excel(s, sheet_name='Cases', index_col=None, header=None, nrows=1, engine='xlrd')
    update_date = str(update_date.iloc[0, 0])[13:]+filesource_caveat


    # Cases Data
    df = pd.read_excel(s, sheet_name='Cases', index_col=None, skiprows=3, header=0, engine='xlrd')

    # Jan 1st onwards
    df = df.loc[df['date_report'] >= datetime.strptime('2020-01-01', '%Y-%m-%d')]

    # Remove repatriated (cruise ships)
    df = df.loc[df['province'] != 'Repatriated']

    # Keep only key columns
    keep_cols = ['provincial_case_id', 'age', 'sex', 'health_region', 'province', 'date_report', 'report_week',
                 'travel_yn', 'travel_history_country', 'additional_info']

    df = df[keep_cols]


    # Deaths
    deaths = pd.read_excel(s, sheet_name='Mortality', index_col=None, skiprows=3, header=0, engine='xlrd')
    keep_cols_death = ['death_id', 'age', 'sex', 'health_region', 'province', 'date_death_report',
                       'additional_info']
    deaths = deaths[keep_cols_death]

    # Format datetime
    deaths['date_death_report'] = deaths['date_death_report'].dt.strftime('%d-%m-%Y')

    deaths.sort_values('date_death_report', ascending=False, inplace=True)

    # Remove repatriated (cruise ships)
    deaths = deaths.loc[deaths['province'] != 'Repatriated']

    return df, deaths, update_date
import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)

st.title('My Cool Name App')

with st.sidebar:
    input_name = st.text_input('Enter a name:', 'Mary')
    year_input = st.slider('Year', min_value=1800, max_value=2023, value=2000)
    n_names = st.radio('Number of names per sex', [3, 5, 10])

tab1, tab2, tab3 = st.tabs(['Names', 'Year','one-click Wonders'])

with tab1:
    # input_name = st.text_input('Enter a name:', 'Mary')
    name_data = data[data['name']==input_name].copy()
    fig = px.line(name_data, x='year', y='count', color='sex')
    st.plotly_chart(fig)

with tab2:
    fig2 = top_names_plot(data, year=year_input, n=n_names)
    st.plotly_chart(fig2)

    st.write('Unique Names Table')
    output_table = unique_names_summary(data, year_input)
    st.data_editor(output_table)

    # Create a downloadable CSV file
    csv_data = output_table.to_csv(index=False)
    
    # Add a download button
    st.download_button(
        label="Download Unique Names Data as CSV",
        data=csv_data,
        file_name=f'unique_names_{year_input}.csv',
        mime='text/csv'
    )

    # Gender Popularity Over Time
st.subheader("Gender Popularity Over Time")

# Input for Year Range
year_range = st.slider('Select a year range:', min_value=1880, max_value=2023, value=(1950, 2000))

# Filter the dataset based on the year range
gender_trend_data = data[(data['year'] >= year_range[0]) & (data['year'] <= year_range[1])]

# Group by year and sex, and sum the counts
gender_trend = gender_trend_data.groupby(['year', 'sex'])['count'].sum().reset_index()

# Create the line chart
gender_fig = px.line(
    gender_trend,
    x='year',
    y='count',
    color='sex',
    title=f"Gender Popularity from {year_range[0]} to {year_range[1]}",
    labels={'count': 'Count of Names', 'year': 'Year', 'sex': 'Gender'}
)
st.plotly_chart(gender_fig)

with tab3:
    st.write("One-Hit Wonders Analysis")

    selected_year = st.slider('Select a year for One-Hit Wonders', min_value=1880, max_value=2023, value=2000)
    ohw_year_data = ohw_data[ohw_data['year'] == selected_year]

    if not ohw_year_data.empty:
        st.write(f"One-Hit Wonders in {selected_year}")
        st.dataframe(ohw_year_data[['name', 'sex', 'count']].sort_values('count', ascending=False))
    else:
        st.write(f"No one-hit wonders found for {selected_year}.")

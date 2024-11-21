import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import requests
from io import BytesIO
from my_plots import *
import streamlit as st

# Load the dataset
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
                df.columns = ['name', 'sex', 'count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

# Function to convert DataFrame to CSV for download
@st.cache_data
def convert_df_to_csv(dataframe):
    # Convert the DataFrame to CSV format and encode it
    return dataframe.to_csv(index=False).encode("utf-8")

# Load the data
data = load_name_data()

# Sidebar widgets
with st.sidebar:
    input_name = st.text_input('Enter a name:', 'Mary')
    year_input = st.slider('Year', min_value=1880, max_value=2023, value=2000)
    n_names = st.radio('Number of names per sex:', [3, 5, 10])
    decade = st.selectbox(
        "Select a Decade:",
        options=["1880s", "1890s", "1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
    )

# Parse the selected decade into a range of years
start_year = int(decade[:4])
end_year = start_year + 9

# Filter the data for the selected decade
decade_data = data[(data['year'] >= start_year) & (data['year'] <= end_year)]

# Tabs for visualization
tab1, tab2 = st.tabs(['Names', 'Year'])

# Tab 1: Name trends
with tab1:
    st.header(f"Trends for {input_name} in {decade}")
    name_decade_data = decade_data[decade_data['name'].str.lower() == input_name.lower()]
    if name_decade_data.empty:
        st.warning(f"No data available for the name '{input_name}' in {decade}.")
    else:
        fig = px.line(name_decade_data, x='year', y='count', color='sex')
        st.plotly_chart(fig)

# Tab 2: Yearly Insights and Download Button
with tab2:
    st.header(f"Top Names in {year_input}")

    # Filter data for the selected year
    year_data = data[data['year'] == year_input]

    # Debugging: Show the filtered data
    st.write(f"Filtered data for year {year_input} (Preview):", year_data.head())

    if year_data.empty:
        st.warning(f"No data available for the year {year_input}. Please choose another year.")
    else:
        # Generate the graph
        fig2 = top_names_plot(year_data, n=n_names)
        st.plotly_chart(fig2)

    # Display unique names summary table
    st.write("Unique Names Table")
    output_table = unique_names_summary(data, year_input)
    st.data_editor(output_table)

    # Add a download button for the selected year's data
    csv = convert_df_to_csv(year_data)
    st.download_button(
        label="Download Data for Selected Year",
        data=csv,
        file_name=f"names_data_{year_input}.csv",
        mime="text/csv",
    )


 
import streamlit as st
import pandas as pd
import folium
from folium import Choropleth
from streamlit_folium import st_folium
import geopandas as gpd



APP_TITLE = 'Data Science For Humanities - Data Project'
APP_SUB_TITLE = 'Causal Relationship Between Trust in Government, Population Vaccination, and Epidemic Evolution'
APP_ABOUT = "This website is part of the Data Science for Humanities course at the University of Luxembourg. It aims to explore the causal relationship between trust in government, population vaccination, and epidemic evolution. The data used in this project is publicly available and comes from various sources. This project was realized by Réda Belcaid and Thierry Guiot."

trust_metrics = {
    'TRUST_NG': 'Trust in National Government',
    'TRUST_LG': 'Trust in Local Government',
    'TRUST_CS': 'Trust in Civil Service',
    'PE_SWGD': 'Trust in Political efficacy',
    'SAD': 'Satisfaction with Democracy'
}


# ----- Sidebar -----
def chooseMetric():
    metrics_list = list(trust_metrics.values())
    trustMetric = st.sidebar.selectbox('Trust metric', metrics_list, 0)
    trustMetric = list(trust_metrics.keys())[list(trust_metrics.values()).index(trustMetric)]
    return trustMetric

def chooseYear():
    years_list = [2020, 2021, 2022, 2023, 2024]
    year = st.sidebar.selectbox('Year (only for Covid data)', years_list, 1)
    return year


# ----- Pages content -----
def displayTrustMap(column, df):
    
    # Load the world map
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Merge dataset with the world map
    world_merged = world.merge(df, how='left', left_on='name', right_on='name')
    # replace null values for OBS_VALUE with 'unknown'
    world_merged[column] = world_merged[column].fillna("Country not in project's scope")
    # replace 0 values for OBS_VALUE with 'unknown'
    world_merged[column] = world_merged[column].replace(0, 'unknown')

    # Create a folium map
    map = folium.Map(location=[50, 35], zoom_start=3)

    # Add choropleth layer
    choropleth = Choropleth(
        geo_data=world_merged,
        name='choropleth',
        data=df,
        columns=['name', column],
        key_on='feature.properties.name',
        fill_color='PuRd',
        fill_opacity=0.8,
        line_opacity=0.3,
        nan_fill_color='white',
        legend_name=column
    )
    choropleth.geojson.add_to(map)

    df_indexed = df.set_index('name')
    # Add tooltip functionality
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(fields=['name', column],
                                                                aliases=['Country', trust_metrics[column]],
                                                                labels=True))
    return map

def displayCovidMap(year, df):


    # Only keep the rows for the selected year
    df = df[df['year'] == year]
    
    # Load the world map
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Merge dataset with the world map
    world_merged = world.merge(df, how='right', left_on='name', right_on='location')
    # replace null values with 'unknown'
    world_merged['total_cases_per_million'] = world_merged['total_cases_per_million'].fillna("Unknown")
    # replace 0 values with 'unknown'
    world_merged['total_cases_per_million'] = world_merged['total_cases_per_million'].replace(0, 'Unknown')

    # Create a folium map
    map = folium.Map(location=[50, 35], zoom_start=3)

    # Add choropleth layer
    choropleth = Choropleth(
        geo_data=world_merged,
        name='choropleth',
        data=df,
        columns=['location', 'total_cases_per_million'],
        key_on='feature.properties.location',
        fill_color='BuGn',
        fill_opacity=0.8,
        line_opacity=0.3,
        nan_fill_color='white',
        legend_name='total_cases_per_million'
    )
    choropleth.geojson.add_to(map)

    df_indexed = df.set_index('location')
    # Add tooltip functionality
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(fields=['location', 'total_cases_per_million'],
                                                                aliases=['Country', 'total_cases_per_million'],
                                                                labels=True))
    return map


# ----- Main -----
def main():

    st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': APP_ABOUT
    }
    )
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    st.caption('Réda Belcaid & Thierry Guiot')

    # Load datasets
    df_trust = pd.read_csv('trust_by_country.csv')
    df_covid = pd.read_csv('covid_data.csv')
    trust_metric = chooseMetric()
    year = chooseYear()


    st.title("Trust and Vaccination")
    col1, col2 = st.columns(2)
    with col1:
        trust_description = "*" + trust_metrics[trust_metric] + "* - year 2021"
        st.write(trust_description)
        st_folium(displayTrustMap(trust_metric, df_trust), width=800, height=600)
    with col2:
        covid_description = "*Percentage of population vaccinated* - year " + str(year)
        st.write(covid_description)
        st_folium(displayCovidMap(year, df_covid), width=800, height=600)

    st.title("Correlation")
    st.write("Correlation matrix between trust metrics and vaccination rates (for the year 2021 only).")
    st.image('imgs/correlation_matrix.png', use_column_width=True)
    


if __name__ == "__main__":
    main()



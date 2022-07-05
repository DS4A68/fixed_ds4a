from turtle import width
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas
import branca
from shapely import wkt
from shapely.geometry.multipolygon import MultiPolygon
import re
from unicodedata import normalize
from folium.plugins import TimeSliderChoropleth
import datetime
import json



st.set_page_config(layout = "wide")
df_time = pd.read_csv("df_time_all.csv")
df_time = df_time.drop(df_time.columns.to_list()[0],axis =1)
df_time['FECHA HECHO'] = pd.to_datetime(df_time['FECHA HECHO'])



#data = pd.read_excel("Reporte__Delitos_sexuales_Polic_a_Nacional (1) (2).xlsx", nrows= 10000)
#Plto with full time series. 


#INITIAL PLOT 
df_time_big_front = df_time.groupby(pd.Grouper(key = 'FECHA HECHO',freq='M')).sum().reset_index()
plot_time = px.line(
    df_time_big_front,
    x = 'FECHA HECHO',
    y = 'CANTIDAD'
)
plot_time.update_yaxes(title_text = "Cantidad de eventos")
plot_time.update_xaxes(title_text = "Tiempo ")
plot_time.update_layout(title = " Progresion de crimenes en el tiempo " ,width = 1200)



#TOP LEFT PLOT - WEEKDAY

df_time_weekday =  df_time.groupby(df_time["FECHA HECHO"].dt.weekday).sum().reset_index()
df_time_weekday['WEEKDAY'] =  ['LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO']
weekday_plot = px.bar(
    df_time_weekday,
    x = 'WEEKDAY',
    y = 'CANTIDAD' 
) 
weekday_plot.update_layout(
    title = "Crimenes por día de la semana",
    xaxis_title = "Day de la Semana",
    yaxis_title = "Cantidad de eventos",
    width = 1000
)




df_time_month_year = df_time.copy()
df_time_month_year['MONTH'] = df_time_month_year['FECHA HECHO'].dt.month
df_time_month_year['YEAR'] = df_time_month_year['FECHA HECHO'].dt.year


month_year_plot = px.area(df_time_month_year,x = 'YEAR', y ='CANTIDAD',color = 'MONTH')
month_year_plot.update_layout(
    xaxis_title = 'Año',
    yaxis_title = 'Cantidad de eventos',
    title = "Casos por año y mes",
    width = 1000
)




forecast_data = pd.read_csv('forecast.csv')
forecast_data['y-m'] = pd.to_datetime(forecast_data['y-m'])
plot_forecast = px.line(
    forecast_data,
    x = 'y-m',
    y = 'CANTIDAD',
    color = 'note'
)
plot_forecast.add_vline(x = datetime.datetime(year = 2022,month = 2, day = 1), line_dash = 'dash' )
plot_forecast.update_layout(title = " Forecast " ,width = 1200)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #




# Correlation 
corr_sx_intra = pd.read_csv("correlation_sx_intraf.csv")
fig_corr = px.scatter(corr_sx_intra, x="CANTIDAD_DELITOS_SEXUALES", y="CANTIDAD_DELITOS_INTRAFAMI",trendline='ols',trendline_color_override="red")



select_box = st.sidebar.selectbox("Despliege esta lista de opciones para ver los distintos analisis",("Como funciona esta apliación","Analisis tiempo","Dsitribuciones",'Geoanalisis','Creadores'))
#st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")


if select_box == "Como funciona esta apliación":
    st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")
    st.title("Como funciona esta aplicación")
    st.markdown("Bienvenido a nuestra aplicación. Mira el siguiente video si es la primera vez que entras o si deseas recordar como funciona!")
    st.markdown("Gracias")


    url = "https://www.youtube.com/watch?v=2S1iTgq8Qks"
    st.video(url)

# ---------------------------------------------------------------------------------------------

if select_box == "Analisis tiempo":
    st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")
    st.title("Progresion de los Delitos En Colombia")
    with st.container():
        st.plotly_chart(plot_time,use_conatiner_width = True)
    st.markdown("<hr>",unsafe_allow_html = True)
    col1,col2 =  st.columns(2)
    with col1:
        st.plotly_chart(weekday_plot,use_conatiner_width = True)
    with col2:
        st.plotly_chart(month_year_plot,use_container_width =True)
    st.markdown("<hr>",unsafe_allow_html = True)
    st.plotly_chart(plot_forecast)

    



# ---------------------------------------------------------------------------------------------

if select_box == "Dsitribuciones":
    
    st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")
    st.title("Dsitribuciones")
    
    
    
    filter_dept = st.selectbox("Departamento",sorted(corr_sx_intra['DEPARTAMENTO'].unique()))


    df_filtered = corr_sx_intra[corr_sx_intra['DEPARTAMENTO'] == filter_dept]

    col_a, col_b=  st.columns(2)
    with col_a:
        fig_a = px.box(df_filtered, y ='CANTIDAD_DELITOS_SEXUALES')
        st.plotly_chart(fig_a)
    with col_b:
        fig_b = px.box(df_filtered, y ='CANTIDAD_DELITOS_INTRAFAMI')
        st.plotly_chart(fig_b)

    st.markdown("<hr>",unsafe_allow_html = True)
    
    col_1,col_2 =  st.columns(2)
    with col_1:
        st.plotly_chart(fig_corr,use_container_width =True)
    
    
    with col_2: 
        html_plot_info = """<h2> Trendline :  <i> Y  = 4.70794  X - 96.547</i></h2>
        <h2> <h:math> R^2 </h:math> : 0.864 </h2>
        <h2> Correlation Matrix : <h2>[1, 0.92967626]<br>[0.92967626, 1] </h2>
        """
        st.markdown(html_plot_info,unsafe_allow_html = True)





# ---------------------------------------------------------------------------------------------



if select_box == 'Geoanalisis':
    st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")
    st.title("Analisis Geografico")

    _merged_ = geopandas.read_file('geojson\_merged_.geojson')
    _orig_ = geopandas.read_file('geojson\_orig_.geojson')
    dept_count_grouped_year = pd.read_csv("geojson\dept_count_grouped_year.csv")

    with open('geojson\colors.json') as file:
        colors_dict = json.load(file)


    map_ = folium.Map(location=[6.258679441576251, -75.55570032068375],
                        zoom_start=7,
                        tiles="OpenStreetMap")
    g = TimeSliderChoropleth(
        _orig_.to_json(),
        styledict=colors_dict
    ).add_to(map_)
    folium.GeoJson(_orig_.to_json(), style_function = lambda x: {
        'color': 'black',
        'weight':2,
        'fillOpacity':0
    }, tooltip=folium.GeoJsonTooltip(
            fields=['NOMBRE_DPT'],
            aliases=['DEPARTAMENTO'], 
            localize=True
        )).add_to(map_)


    st.image("years.jpg",width = 1300)
    st_data_ = st_folium(map_,width = 1300,height = 800)



# ---------------------------------------------------------------------------------------------



one_dani :str ="""
"<a href="https://www.linkedin.com/in/dlopesierra/">Daniel Lopesierra</a>"
"""
one_juan :str ="""
"<a href="https://www.linkedin.com/in/juan-pablo-c%C3%A9spedes-ortiz-4b1778209/">Juan Céspedes</a>"
"""
one_alejo :str ="""
"<a href="https://www.linkedin.com/in/juan-pablo-c%C3%A9spedes-ortiz-4b1778209/">Alejandro Velez</a>"
"""



email_juan = """Jpcespedeso@unal.edu.co"""
email_alejo = """alejandrovelez1995@hotmail.com"""
email_dani = """dlopesierraz@gmail.com"""

if select_box == 'Creadores':
    st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")
    st.title("Creadroes:")
    st.markdown("<hr>", unsafe_allow_html =True)


    with st.container():
        col_1,col_2,col_3 = st.columns(3)
        with col_1:
            st.image("juan.jpg",caption = 'Juan Céspedes' )
        with col_2:
            st.markdown("<h2>About</h2>",unsafe_allow_html = True) 
            st.markdown("Joven competitivo que se caracteriza por tener una gran motivación para seguir perfeccionando habilidades y por crecer profesionalmente. Con capacidades para trabajar en equipo, liderazgo y amplio sentido de pertenencia. Es creativo y visionario.Actualmente cuenta con especial interés en Big Data y analítica, Así como en temas de producción y finanzas. Se ha desempeñado como dirigente scout de un grupo de jóvenes de 13 a 16 años. Persona proactiva, responsable y con grandes calidades morales. Ha hecho parte de grandes proyectos de consultoría con empresas como Cotrafa, y la universidad Nacional de Colombia.")
        with col_3:
            st.markdown("<h2>Contact</h2>",unsafe_allow_html = True)
            
            st.markdown("<h4> Linked in  : </h4>",unsafe_allow_html =True)
            st.markdown(one_juan,unsafe_allow_html =True)

            st.markdown("<h4> Email  : </h4>",unsafe_allow_html =True)
            st.markdown(email_juan,unsafe_allow_html =True)
            
            st.markdown("<h4> Phone : </h4> 57+3154940283",unsafe_allow_html = True)
    
    st.markdown("<hr>", unsafe_allow_html =True)
    
    with st.container():
        col_1,col_2,col_3 = st.columns(3)
        with col_1:
            st.image("daniel.jpg",caption = 'Daniel Lopesierra' )
        with col_2:
            st.markdown("<h2>About</h2>",unsafe_allow_html = True) 
            st.markdown("Professional with more than 6 years of experience across different Finance and Supply Chain functions. I have experience in financial planning, analysis and controlling, as well as supply chain planning in multinational companies. I've worked in different industries such as CPG, Pharma and I'm currently working for Adidas in the Retail industry.")
        with col_3:
            st.markdown("<h2>Contact</h2>",unsafe_allow_html = True)
            
            st.markdown("<h4> Linked in  : </h4>",unsafe_allow_html =True)
            st.markdown(one_dani,unsafe_allow_html =True)

            st.markdown("<h4> Email  : </h4>",unsafe_allow_html =True)
            st.markdown(email_dani,unsafe_allow_html =True)
            
            st.markdown("<h4> Phone : </h4> 57+3154007070",unsafe_allow_html = True)
    

    st.markdown("<hr>", unsafe_allow_html =True)

    with st.container():
        col_1,col_2,col_3 = st.columns(3)
        with col_1:
            st.image("Alejo.jpg",caption = 'Alejandro Vélez' )
        with col_2:
            st.markdown("<h2>About</h2>",unsafe_allow_html = True) 
            st.markdown("Bachelor in international business with several years worth of experience on different fields that have led to develop a very holistic insight of modern companies. Focused on teamwork and goal accomplishing. Into data analystics using of SQL and Python.")
        with col_3:
            st.markdown("<h4>Contact</h4>",unsafe_allow_html = True)
            
            st.markdown("<h4> Linked in  : </h4>",unsafe_allow_html =True)
            st.markdown(one_alejo,unsafe_allow_html =True)

            st.markdown("<h4> Email  : </h4>",unsafe_allow_html =True)
            st.markdown(email_alejo,unsafe_allow_html =True)
            
            st.markdown("<h4> Phone : </h4> 57+3217916049",unsafe_allow_html = True)
            
            
        





    


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
data_time = pd.read_csv('data_time.csv')



#data = pd.read_excel("Reporte__Delitos_sexuales_Polic_a_Nacional (1) (2).xlsx", nrows= 10000)
#Plto with full time series. 





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
plot_forecast.update_layout(title = " Forecast " ,width = 1350)




#Comparacion

log_comp = pd.read_csv('log_comp.csv')


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #




# Correlation 
corr_sx_intra = pd.read_csv("correlation_sx_intraf.csv")
fig_corr = px.scatter(corr_sx_intra, x="CANTIDAD_DELITOS_SEXUALES", y="CANTIDAD_DELITOS_INTRAFAMI",trendline='ols',trendline_color_override="red")



select_box = st.sidebar.selectbox("Despliege esta lista de opciones para ver los distintos analisis",(
    "Como funciona esta apliación",
    "Comportamiento por tiempo y genero",
    "Relación con la violencia domestica",
    'Progresión geográfica',
    'Creadores'))
#st.title("Analisis estadisitco  -  Delitos sexuales en Colombia")


if select_box == "Como funciona esta apliación":
    st.title("Analisis estadísitco  -  Delitos sexuales en Colombia")
    st.title("Como funciona esta aplicación")
    st.markdown("Bienvenido a nuestra aplicación. Mira el siguiente video si es la primera vez que entras o si deseas recordar como funciona!")
    st.markdown("Gracias")


    url = "https://www.youtube.com/watch?v=2S1iTgq8Qks"
    st.video(url)

# ---------------------------------------------------------------------------------------------

if select_box == "Comportamiento por tiempo y genero":
    st.title("Analisis estadísitco  -  Delitos sexuales en Colombia")
    st.title("Comportamiento por tiempo y genero")
    with st.container():



        #st.plotly_chart(plot_time,use_conatiner_width = True)

        page_names_ = ['Por departamento','Total']
        page_ = st.radio("Puedes filtrar los datios por departamento o ver el total por País",page_names_)
        st.write("Escala escogida", page_)

        if page_ == 'Total':
            data_time_ = data_time.groupby('MONTH-YEAR')['CANTIDAD_DELITOS_SEXUALES'].sum().to_frame().reset_index()
            Total_ = px.line(data_time_,x = 'MONTH-YEAR', y = 'CANTIDAD_DELITOS_SEXUALES',width = 1350)
            Total_.update_layout(
            title = "Progresion de crimenes",
            width = 1000)
            st.plotly_chart(Total_)

        else: 
            filter_dept_ = st.selectbox("Departamento", sorted(data_time['DEPARTAMENTO'].unique()))
            data_time_filtered = data_time[data_time['DEPARTAMENTO'] == filter_dept_]

            filt_plot = px.line(data_time_filtered,x= 'MONTH-YEAR', y = 'CANTIDAD_DELITOS_SEXUALES',width = 1350)
            filt_plot.update_layout(
            title = "Progresion de crimenes",
            width = 1000)            
            st.plotly_chart(filt_plot)
    
    st.markdown("<hr>",unsafe_allow_html = True)


    column1,column2 = st.columns(2)

    with column1:
        capturas_df = pd.read_csv("capturas_genero.csv")
        cap_plot = px.bar(capturas_df,x = 'index', y = 'GENERO')
        cap_plot.update_layout(
        title = "Capturas por genero en 2022",
        width = 1000)            
        st.plotly_chart(cap_plot)
    with column2:
        rep_casos = pd.read_csv("rep_casos_gen.csv")
        feme_mas_ = px.bar(rep_casos, x ='Año', y = rep_casos.columns[2:] )
        feme_mas_.update_layout(
        title = "Reportes de Casos por Genero",
        width = 1000)  
        st.plotly_chart(feme_mas_)

    
    
    
    st.markdown("<hr>",unsafe_allow_html = True)
    col1,col2 =  st.columns(2)
    with col1:
        st.plotly_chart(weekday_plot,use_conatiner_width = True)
    with col2:
        st.plotly_chart(month_year_plot,use_container_width =True)
    st.markdown("<hr>",unsafe_allow_html = True)
    st.plotly_chart(plot_forecast)

    



# ---------------------------------------------------------------------------------------------

if select_box == "Relación con la violencia domestica":
    
    st.title("Analisis estadísitco  -  Delitos sexuales en Colombia")
    st.title("Relación con la violencia domestica")
    
    
    page_names = ['Real','Logarítmica']
    page = st.radio("Puedes escoger Si ver en escala logaritimica o Real ",page_names)
    st.write("Escala escogida: ", page)

    if page == 'Real':
        real_ = px.line(log_comp,x = 'MONTH-YEAR', y = ['CANTIDAD_DELITOS_INTRAFAMI','CANTIDAD_DELITOS_SEXUALES'],width = 1350)

        st.plotly_chart(real_)
    else:

        log = px.line(log_comp,x = 'MONTH-YEAR', y = ['CANTIDAD_DELITOS_INTRAFAMI_log','CANTIDAD_DELITOS_SEXUALES_log'],width = 1350)
        st.plotly_chart(log)










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
        html_plot_info = """<h2> Tendencia :  <i> Y  = 4.70794  X - 96.547</i></h2>
        <h2> <h:math> R^2 </h:math> : 0.864 </h2>
        <h2> Matriz de Correlación : <h2>[1, 0.92967626]<br>[0.92967626, 1] </h2>
        """
        st.markdown(html_plot_info,unsafe_allow_html = True)





# ---------------------------------------------------------------------------------------------



if select_box == 'Progresión geográfica':
    st.title("Analisis estadísitco  -  Delitos sexuales en Colombia")
    st.title("Progresión geográfica")

    _merged_ = geopandas.read_file('geojson\_merged_.geojson')
    _orig_ = geopandas.read_file('geojson\_orig_.geojson')
    dept_count_grouped_year = pd.read_csv("geojson\dept_count_grouped_year.csv")

    with open('geojson\colors.json') as file:
        colors_dict = json.load(file)


    map_ = folium.Map(location=[6.258679441576251, -75.55570032068375],
                        zoom_start=5,
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


   
    st.success(" Despus de hacer Zoom o desplazarte por el mapa, espera unos segundos para que cargue correctamente ")

    col_1_,col_2_,col_3_ =  st.columns(3)
    with col_2_:
        st.image("years.jpg",width = 700)
        #st.plotly_chart(fig_corr,use_container_width =True)
        st_data_ = st_folium(map_,width = 800,height = 600)



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
    st.title("Analisis estadísitco  -  Delitos sexuales en Colombia")
    st.title("Creadroes:")
    st.markdown("<hr>", unsafe_allow_html =True)


    with st.container():
        col_1,col_2,col_3 = st.columns(3)
        with col_1:
            st.image("Juan.jpg",caption = 'Juan Céspedes' )
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
            st.markdown("Profesional con más de 6 años de experiencia a lo largo de diferentes funciones y roles de Finanzas y cadena de suministros. Tengo experiencia en planeamiento financiero, análisis y control del mismo modo, en planeamiento de cadenas de suministros para organizaciones multinacionales. He trabajado en diferentes industrias como CPG, Pharma y actualmente trabajo para Adidas en la industria de Retail.")
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
            st.markdown("Profesional en negocios internacionales con varios años de experiencia en diferentes áreas que le han llevado a tener un entendimiento muy holístico de las organizaciones modernas. Enfocado en el trabajo de equipo y cumplimiento de los objetivos. Técnicamente especializado en el manejo de Python y SQL para la ingeniería Datos")
        with col_3:
            st.markdown("<h4>Contact</h4>",unsafe_allow_html = True)
            
            st.markdown("<h4> Linked in  : </h4>",unsafe_allow_html =True)
            st.markdown(one_alejo,unsafe_allow_html =True)

            st.markdown("<h4> Email  : </h4>",unsafe_allow_html =True)
            st.markdown(email_alejo,unsafe_allow_html =True)
            
            st.markdown("<h4> Phone : </h4> 57+3217916049",unsafe_allow_html = True)
            
            
        





    


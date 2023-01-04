import streamlit as st
import pandas as pd
from PIL import Image
import requests

# Tools

import folium
from tqdm import tqdm
from haversine import haversine, Unit

from geopandas import datasets, GeoDataFrame, read_file, points_from_xy


from streamlit_folium import folium_static

# funciones
def GetLatLon2(Address,YOUR_API_KEY):

    url2_geocode  = f'https://geocode.search.hereapi.com/v1/geocode?q={Address}&apiKey='+YOUR_API_KEY

    try:
        response = requests.get(url2_geocode).json()
        CleanAddress = response['items'][0]['title'].upper()
        LAT = response['items'][0]['position']['lat']
        LON = response['items'][0]['position']['lng']
        results = [CleanAddress,round(LAT,7),round(LON,7)]
    except:
        results = ['NotFound','NA','NA']
    return results

def GetLatLon2_google(Address,YOUR_API_KEY):

    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={Address}&key={YOUR_API_KEY}'
    try:
        j = requests.get(api_url).json()
        CleanAddress = str(j['results'][0]['formatted_address']).upper()
        LAT = j['results'][0]['geometry']['location']['lat']
        LON = j['results'][0]['geometry']['location']['lng']
        results = [CleanAddress,round(LAT,7),round(LON,7)]
    except:
        results = ['NotFound','NA','NA']
    return results,j

# Calc Distance
def cal_dist(geo_source,point2,unit):


    if unit == 'Km':
        distance = haversine(geo_source, point2,Unit.KILOMETERS)
    elif unit == 'm':
        distance = haversine(geo_source, point2,Unit.METERS)
    elif unit == 'miles':
        distance = haversine(geo_source, point2,Unit.MILES)

    return distance

# Locations within radius
def distance_estac(geo_source,df,radio,unit):


    distancia = []
    source = []


    for i in tqdm(range(len(df)),colour = 'green'):
        distancia.append(cal_dist(geo_source,df['POINT'][i],unit))
        source.append(geo_source)

    new_df = df.copy()
    new_df['SOURCE'] = source
    new_df['DISTANCE'] = distancia
    new_df = new_df[new_df['DISTANCE']<=radio]
    new_df = new_df.reset_index()
    new_df = new_df.drop(columns ='index')
    return new_df.sort_values(by='DISTANCE',ascending=True)

# Create centroid pairs
def transform_df_map(df_temp):

    coordenadas = []

    for i in range(len(df_temp)):

        try :

            coord = float(df_temp['LAT'][i]),float(df_temp['LNG'][i])
            coordenadas.append(coord)
        except :
            coordenadas.append('EMPTY')
    df_temp['POINT'] = coordenadas
    df_temp = df_temp[df_temp['POINT']!='EMPTY']
    df_temp = df_temp.reset_index()
    df_temp = df_temp.drop(columns = 'index')
    new_df = df_temp.copy()

    return new_df

def marker_rest(df,mapa,unit,oil,icono):

    df = df[df['Producto']==oil]
    df = df.reset_index()
    df = df.drop(columns = 'index')

    for i in range(len(df)):

        if df['Precio'][i]==df['Precio'].min():

            html =  f"""<b>MARCA:</b> {df.Bandera[i]} <br>
                    <b>NAME:</b> {df.Nombre_comercial[i]} <br>
                    <b>PRODUCTO:</b> {df.Producto[i]} <br>
                    <b>PRECIO:</b> {df.Precio[i]} <br>
                    <b>DISTANCE:</b> {round(df.DISTANCE[i],2)}<br>
                    <b>DIRECCION:</b> {df.Direccion[i]}<br>
                    <b>UNIT:</b> {unit}<br>"""
            iframe = folium.IFrame(html,figsize=(6, 3))
            popup = folium.Popup(iframe)




            folium.Marker(location=[float(df['LAT'][i]),float(df['LNG'][i])],
                               icon=folium.Icon(color='darkgreen', icon_color='white',
                               icon=icono, prefix='glyphicon'),
                               popup = popup).add_to(mapa)

        elif df['Precio'][i]==df['Precio'].max():

            html =  f"""<b>MARCA:</b> {df.Bandera[i]} <br>
                    <b>NAME:</b> {df.Nombre_comercial[i]} <br>
                    <b>PRODUCTO:</b> {df.Producto[i]} <br>
                    <b>PRECIO:</b> {df.Precio[i]} <br>
                    <b>DISTANCE:</b> {round(df.DISTANCE[i],2)}<br>
                    <b>DIRECCION:</b> {df.Direccion[i]}<br>
                    <b>UNIT:</b> {unit}<br>"""
            iframe = folium.IFrame(html,figsize=(6, 3))
            popup = folium.Popup(iframe)



            folium.Marker(location=[float(df['LAT'][i]),float(df['LNG'][i])],
                               icon=folium.Icon(color='darkred', icon_color='white',
                               icon=icono, prefix='glyphicon'),
                               popup =popup).add_to(mapa)
        else :
            html =  f"""<b>MARCA:</b> {df.Bandera[i]} <br>
                    <b>NAME:</b> {df.Nombre_comercial[i]} <br>
                    <b>PRODUCTO:</b> {df.Producto[i]} <br>
                    <b>PRECIO:</b> {df.Precio[i]} <br>
                    <b>DISTANCE:</b> {round(df.DISTANCE[i],2)}<br>
                    <b>DIRECCION:</b> {df.Direccion[i]}<br>
                    <b>UNIT:</b> {unit}<br>"""
            iframe = folium.IFrame(html,figsize=(6, 3))
            popup = folium.Popup(iframe)



            folium.Marker(location=[float(df['LAT'][i]),float(df['LNG'][i])],
                               icon=folium.Icon(color='orange', icon_color='white',
                               icon=icono, prefix='glyphicon'),
                               popup =popup).add_to(mapa) #<font-awesome-icon icon="fa-regular fa-gas-pump" />

    return

#inicio de aplicación
# key = st.text_input("Pon un api key de geolocalización")
YOUR_API_KEY = '_UYTHcJDeDZmNidmEtfH-RhrQrmMrIURdHGwzIq324Q'

image = Image.open('perfil.jpg')

st.sidebar.markdown('Nicolas Gutierrez')
st.sidebar.image(image , caption="Aplicación de la gasolinería de aceite más cercana a tí",width = 250)
app_mode = st.sidebar.selectbox("escoge que quieres ver", ["Aplicación","Sobre mí"])


if app_mode == 'Aplicación':

    st.title('Aplicación de la gasolinería de aceite más cercana a tí')
    st.markdown('Aplicación creada para buscar un lugar y ver cuales son las gasolinerías cercanas a tí y que puedas mirar sus precios. :)')

    df_map = pd.read_csv('DF_STATIONS.csv')
    cities =  list(df_map['Municipio'].unique())

    c1,c2,c3,c4,c5 = st.columns((1,6,6,6,1))

    choose_city =  c2.selectbox("Escoge la ciudad:", cities)

    central_location = c2.text_input('Lugar específico', 'unac, Medellín')

    DEVELOPER_KEY = YOUR_API_KEY

    if len(central_location) != 0 :

        R = GetLatLon2(central_location,YOUR_API_KEY)
        geo_source = R[1],R[2]

        unit = 'Km'
        rad = c4.slider('Radius',1,3,1)

        df_city = df_map[df_map['Municipio']==choose_city]
        df_city.reset_index(inplace = True)
        df_city.drop(columns = 'index',inplace = True)

        df_city =  transform_df_map(df_city)

        results = distance_estac(geo_source,df_city,rad,unit)
        results = results.reset_index()
        results = results.drop(columns = 'index')
        products =  list(results['Producto'].unique())

        gdf_stores_results = GeoDataFrame(results,
                                            geometry=points_from_xy(results.LNG,results.LAT))


        choose_products =  c3.selectbox("Choose Oil", products)

        if c3.button('MOSTRAR EL MAPA'):

            gdf_stores_results2 = gdf_stores_results[gdf_stores_results['Producto']==choose_products]
            gdf_stores_results2 = gdf_stores_results2.reset_index()
            gdf_stores_results2 = gdf_stores_results2.drop(columns = 'index')
            icono = "usd"

            m = folium.Map([geo_source[0],geo_source[1]], zoom_start=15)

            # Circle
            folium.Circle(
            radius=int(rad)*1000,
            location=[geo_source[0],geo_source[1]],
            color='green',
            fill='red').add_to(m)

            # Centroid
            folium.Marker(location=[geo_source[0],geo_source[1]],
                                icon=folium.Icon(color='black', icon_color='white',
                                icon="home", prefix='glyphicon')
                                ,popup = "<b>CENTROID</b>").add_to(m)

            marker_rest(gdf_stores_results2,m,unit,choose_products,icono)

            # call to render Folium map in Streamlit
            folium_static(m)
            
elif app_mode == "Sobre mí":
    st.title('Aplicación de la gasolinería de aceite más cercana a tí')
    st.success("Aquí mis redes 👇 ")

    col1,col2,col3,col4 = st.columns((2,1,2,1))
    col1.markdown('* [**LinkedIn**](https://www.linkedin.com/in/nicolas-steven-gutierrez-castiyejo-7a26a3235/)')
    col1.markdown('* [**GitHub**](https://github.com/imnicoo7)')
    col1.markdown('* [**Instagram**](https://www.instagram.com/imnicoo__/)')
    col1.markdown('* [**Twitter**](https://twitter.com/Nicolas76675034)')
    image2 = Image.open('perfil.jpg')
    col3.image(image2,width=230)
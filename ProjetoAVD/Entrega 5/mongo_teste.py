from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import pandas as pd
import requests
import folium
import os 

load_dotenv()    

GEOJSON_URL = ("https://dados.recife.pe.gov.br/dataset/09ae25d3-7330-4fff-af57-9e9191a4c2f6/"
"resource/8d43533d-100b-4de2-9b08-65703d910320/download/"
"distritos-sanitarios-do-recife.geojson")

CSV_URL = ("https://dados.recife.pe.gov.br/dataset/09ae25d3-7330-4fff-af57-9e9191a4c2f6/"
"resource/d8d649d6-5bf7-44af-9686-436162766037/download/"
"distritos-sanitarios-descricao-dos-bairros.csv")

DB_NAME = "Recife"
COLLECTION_NAME = "DistritosSanitarios"

bairros = pd.read_csv(CSV_URL, sep=";")
geojson = requests.get(GEOJSON_URL).json()

nomes_distritos = dict(
    bairros[["distrito_sanitario", "descricao_distrito"]]
    .drop_duplicates()
    .values
)

for feature in geojson["features"]:
    codigo = feature["properties"]["cdistscodi"]
    feature["properties"]["nome_distrito"] = nomes_distritos.get(codigo, "Desconhecido")


# Salva os dados no MongoDB Atlas
mongo_uri = os.getenv("MONGO_UI")
# Create a new client and connect to the server
client = MongoClient(mongo_uri, server_api=ServerApi('1'))

collection = client[DB_NAME][COLLECTION_NAME]

#features = list(collection.find({}, {"_id": 0}))
#geojson = {"type": "FeatureCollection" , "features": features}

mapa = folium.Map(
    location=[-8.05, -34.9],
    zoom_start=11,

    titles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Titles &copy; Esri",
)

folium.GeoJson(
    geojson,
    name="Distritos Sanitários",
    tooltip=folium.GeoJsonTooltip(fields=["nome_distrito"], aliases=["Distrito:"]),
    style_function=lambda feature: {"fillColor": "#3186cc", "color": "#black", "weight": 1, "fillOpacity": 0.4},
).add_to(mapa)

mapa.save("mapa_distritos_sanitarios.html")
print("Mapa salvo em mapa_distritos_sanitarios.html.")


#collection.delete_many({})  # Clear the collection before inserting new data
#collection.insert_many(geojson["features"])  # Insert the GeoJSON features into the collection
#print(f"{len(geojson['features'])} distritos salvos em {DB_NAME}.{COLLECTION_NAME}")

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
"""
Nom ......... : Exercice 4.2
Rôle ........ : changer les données EXIF d'une photo + carte
Auteur ...... : Darius Pourre
Version ..... : V1 du chapitre 4
Licence ..... : L1 informatique 
Cours ....... : Outils informatiques collaboratifs
Compilation . : Streamlit
"""

import streamlit as st
from PIL import Image
import exifread
import piexif
import io
import folium
from streamlit_folium import folium_static
import pandas as pd

# Liste des champs EXIF modifiables et leurs labels en français
modifiable_tags = {
    "Image Make": "Fabricant",
    "Image Model": "Modèle",
    "EXIF DateTimeOriginal": "Date et Heure",
    "Image Software": "Logiciel",
    "GPS GPSLatitude": "Latitude (deg,min,sec)",
    "GPS GPSLongitude": "Longitude (deg,min,sec)",
    "EXIF ExposureTime": "Temps d'exposition (num/denom)",
    "EXIF FNumber": "Ouverture (num/denom)",
    "EXIF ISOSpeedRatings": "ISO"
}

# Noms des fichiers CSV contenant les lieux visités et souhaités
locations_visited_file_path = 'locations_visited.csv'
locations_wishlist_file_path = 'locations_wishlist.csv'

def read_exif(image):
    """Lit les métadonnées EXIF d'une image."""
    exif_data = exifread.process_file(image)
    return {tag: exif_data[tag] for tag in exif_data.keys() if tag in modifiable_tags}

def write_exif(image, new_exif_data):
    """Écrit les nouvelles métadonnées EXIF dans une image."""
    exif_dict = piexif.load(image.info.get("exif", b""))

    for tag, new_value in new_exif_data.items():
        if tag == "EXIF DateTimeOriginal":
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_value.encode('utf-8')
        elif tag == "Image Make":
            exif_dict['0th'][piexif.ImageIFD.Make] = new_value.encode('utf-8')
        elif tag == "Image Model":
            exif_dict['0th'][piexif.ImageIFD.Model] = new_value.encode('utf-8')
        elif tag == "Image Software":
            exif_dict['0th'][piexif.ImageIFD.Software] = new_value.encode('utf-8')
        elif tag == "GPS GPSLatitude":
            try:
                lat_deg, lat_min, lat_sec = map(float, new_value.split(','))
                exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = [(int(lat_deg * 1000000), 1000000), (int(lat_min * 1000000), 1000000), (int(lat_sec * 1000000), 1000000)]
            except ValueError:
                st.error("Format de latitude incorrect. Utilisez le format: deg,min,sec")
        elif tag == "GPS GPSLongitude":
            try:
                lon_deg, lon_min, lon_sec = map(float, new_value.split(','))
                exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = [(int(lon_deg * 1000000), 1000000), (int(lon_min * 1000000), 1000000), (int(lon_sec * 1000000), 1000000)]
            except ValueError:
                st.error("Format de longitude incorrect. Utilisez le format: deg,min,sec")
        elif tag == "EXIF ExposureTime":
            try:
                num, denom = map(int, new_value.split('/'))
                exif_dict['Exif'][piexif.ExifIFD.ExposureTime] = (num, denom)
            except ValueError:
                st.error("Format de temps d'exposition incorrect. Utilisez le format: num/denom")
        elif tag == "EXIF FNumber":
            try:
                num, denom = map(int, new_value.split('/'))
                exif_dict['Exif'][piexif.ExifIFD.FNumber] = (num, denom)
            except ValueError:
                st.error("Format d'ouverture incorrect. Utilisez le format: num/denom")
        elif tag == "EXIF ISOSpeedRatings":
            try:
                exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings] = int(new_value)
            except ValueError:
                st.error("Format ISO incorrect. Utilisez un nombre.")

    exif_bytes = piexif.dump(exif_dict)
    return exif_bytes

def convert_to_degrees(value):
    """Convertit les valeurs EXIF au format deg,min,sec en degrés décimaux."""
    d = value.values[0].num / value.values[0].den
    m = value.values[1].num / value.values[1].den
    s = value.values[2].num / value.values[2].den
    return d + (m / 60.0) + (s / 3600.0)

def read_locations(file_path):
    """Lit les lieux depuis un fichier CSV."""
    df = pd.read_csv(file_path)
    locations = df[['latitude', 'longitude', 'name']].values.tolist()
    return locations

def create_legend_html():
    """Crée le HTML pour la légende de la carte."""
    legend_html = '''
    <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white;
                padding: 10px;
                ">
    <b>Légende</b><br>
    <i class="fa fa-map-marker fa-2x" style="color:red"></i>&nbsp; Lieu de la photo<br>
    <i class="fa fa-map-marker fa-2x" style="color:green"></i>&nbsp; Lieux visités<br>
    <i class="fa fa-map-marker fa-2x" style="color:blue"></i>&nbsp; Lieux souhaités
    </div>
    '''
    return legend_html

def main():
    st.title("Éditeur de Métadonnées EXIF")

    # Téléchargement d'une image par l'utilisateur
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Image téléchargée.', use_column_width=True)

        # Lire les métadonnées EXIF de l'image
        uploaded_file.seek(0)  # Remettre le curseur au début
        exif_data = read_exif(uploaded_file)

        st.write("Métadonnées EXIF actuelles :")
        for tag, label in modifiable_tags.items():
            value = exif_data.get(tag, 'Non disponible')
            st.write(f"{label}: {value}")

        # Générer le formulaire pour éditer les métadonnées EXIF
        st.write("Éditez les métadonnées EXIF :")
        new_exif_data = {}
        for tag, label in modifiable_tags.items():
            current_value = str(exif_data.get(tag, ''))
            new_value = st.text_input(label, current_value)
            new_exif_data[tag] = new_value

        if st.button("Sauvegarder"):
            # Écrire les nouvelles métadonnées EXIF dans l'image
            exif_bytes = write_exif(image, new_exif_data)
            output = io.BytesIO()
            image.save(output, "jpeg", exif=exif_bytes)
            st.download_button(label="Télécharger l'image modifiée", data=output.getvalue(), file_name="output.jpg", mime="image/jpeg")
            st.success("Les métadonnées EXIF ont été mises à jour avec succès.")

        # Lire les lieux visités et souhaités depuis les fichiers CSV
        try:
            visited_locations = read_locations(locations_visited_file_path)
            wishlist_locations = read_locations(locations_wishlist_file_path)

            st.write("Carte des lieux visités et souhaités :")
            gps_map = folium.Map(location=[0, 0], zoom_start=2)

            visited_points = []
            wishlist_points = []

            for lat, lon, name in visited_locations:
                folium.Marker([lat, lon], tooltip=name, icon=folium.Icon(color='green')).add_to(gps_map)
                visited_points.append([lat, lon])

            for lat, lon, name in wishlist_locations:
                folium.Marker([lat, lon], tooltip=name, icon=folium.Icon(color='blue')).add_to(gps_map)
                wishlist_points.append([lat, lon])

            # Relier les points visités entre eux
            if visited_points:
                folium.PolyLine(visited_points, color="green", weight=2.5, opacity=1).add_to(gps_map)

            # Relier les points de la liste de souhaits entre eux
            if wishlist_points:
                folium.PolyLine(wishlist_points, color="blue", weight=2.5, opacity=1).add_to(gps_map)

            # Affichage de la carte avec les coordonnées GPS modifiées de la photo
            gps_latitude = new_exif_data.get("GPS GPSLatitude")
            gps_longitude = new_exif_data.get("GPS GPSLongitude")
            if gps_latitude and gps_longitude:
                try:
                    # Convertir les coordonnées GPS saisies en degrés décimaux
                    lat_deg, lat_min, lat_sec = map(float, gps_latitude.split(','))
                    lon_deg, lon_min, lon_sec = map(float, gps_longitude.split(','))
                    lat = lat_deg + (lat_min / 60.0) + (lat_sec / 3600.0)
                    lon = lon_deg + (lon_min / 60.0) + (lon_sec / 3600.0)
                    folium.Marker([lat, lon], tooltip="Lieu de la photo", icon=folium.Icon(color='red')).add_to(gps_map)
                    gps_map.location = [lat, lon]
                except ValueError:
                    st.error("Format des coordonnées GPS incorrect. Utilisez le format: deg,min,sec")

            # Ajouter la légende à la carte
            legend_html = create_legend_html()
            legend = folium.Marker(
                location=[0, 0],
                icon=folium.DivIcon(html=legend_html)
            )
            gps_map.add_child(legend)

            folium_static(gps_map)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier des lieux : {e}")

if __name__ == "__main__":
    main()

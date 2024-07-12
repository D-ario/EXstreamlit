import streamlit as st
from PIL import Image
import exifread
import piexif
import io

# Liste des champs EXIF modifiables
modifiable_tags = {
    "Image Make": "Fabricant",
    "Image Model": "Modèle",
    "EXIF DateTimeOriginal": "Date et Heure",
    "Image Software": "Logiciel",
    "GPS GPSLatitude": "Latitude (deg,min,sec)",
    "GPS GPSLongitude": "Longitude (deg,min,sec)",
    "GPS GPSAltitude": "Altitude (mètres)",
    "EXIF ExposureTime": "Temps d'exposition (num/denom)",
    "EXIF FNumber": "Ouverture (num/denom)",
    "EXIF ISOSpeedRatings": "ISO"
}

def read_exif(image):
    exif_data = exifread.process_file(image)
    return {tag: exif_data[tag] for tag in exif_data.keys() if tag in modifiable_tags}

def write_exif(image, new_exif_data):
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
        elif tag == "GPS GPSAltitude":
            try:
                exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (int(float(new_value) * 100), 100)
            except ValueError:
                st.error("Format d'altitude incorrect. Utilisez un nombre.")
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

def main():
    st.title("Éditeur de Métadonnées EXIF")

    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Image téléchargée.', use_column_width=True)

        # Lire les métadonnées EXIF
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
            exif_bytes = write_exif(image, new_exif_data)
            output = io.BytesIO()
            image.save(output, "jpeg", exif=exif_bytes)
            st.download_button(label="Télécharger l'image modifiée", data=output.getvalue(), file_name="output.jpg", mime="image/jpeg")
            st.success("Les métadonnées EXIF ont été mises à jour avec succès.")

if __name__ == "__main__":
    main()

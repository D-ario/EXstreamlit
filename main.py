import streamlit as st
from PIL import Image
import piexif
from io import BytesIO

def load_image(image_file):
    img = Image.open(image_file)
    return img

def get_exif_data(img):
    exif_dict = piexif.load(img.info.get('exif', b''))
    return exif_dict

def save_exif_data(img, exif_dict):
    exif_bytes = piexif.dump(exif_dict)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', exif=exif_bytes)
    return img_byte_arr.getvalue()

def display_exif_form(exif_dict, max_ifds=3):
    editable_exif = {}
    ifd_count = 0
    for ifd in exif_dict:
        if ifd_count >= max_ifds:
            break
        st.write(f"## {ifd}")
        for tag in exif_dict[ifd]:
            if tag in piexif.TAGS[ifd]:
                tag_name = piexif.TAGS[ifd][tag]["name"]
                tag_value = exif_dict[ifd][tag]
                widget_id = f"{ifd}_{tag}"
                new_value = st.text_input(f"{tag_name}:", value=str(tag_value), key=widget_id)
                editable_exif[(ifd, tag)] = new_value
        ifd_count += 1
    return editable_exif

def update_exif_data(exif_dict, editable_exif):
    for (ifd, tag), value in editable_exif.items():
        if value.isdigit():
            exif_dict[ifd][tag] = int(value)
        else:
            exif_dict[ifd][tag] = value.encode()
    return exif_dict

st.title("Application d'édition des métadonnées EXIF")

image_file = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg", "png"])

if image_file is not None:
    img = load_image(image_file)
    st.image(img, caption='Image téléchargée', use_column_width=True)

    if 'exif' in img.info:
        exif_data = get_exif_data(img)
        editable_exif = display_exif_form(exif_data, max_ifds=3)  # Limiter à 3 IFD

        if st.button("Mettre à jour les métadonnées"):
            updated_exif_data = update_exif_data(exif_data, editable_exif)
            output_img = save_exif_data(img, updated_exif_data)
            st.download_button(label="Télécharger l'image mise à jour", data=output_img, file_name="updated_image.jpg")
    else:
        st.warning("Cette image ne contient pas de métadonnées EXIF.")

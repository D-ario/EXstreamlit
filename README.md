# Application d'édition des métadonnées EXIF

cette application Streamlit permet de télécharger une image, d'afficher et d'éditer les métadonnées EXIF.

## Pérequis

Assurez-vous d'avoir installé les bibliothèques suivantes :

-'streamlit'
-'pillow'
-'exifread'
-'piexif'
<<<<<<< HEAD
-'exifread'
=======
-'folium'
-'streamlit_folium'
-'pandas'
>>>>>>> 7504060 (Sur la branche main)

Vous pouvez installer les dépendances en utilisant les fichier 'requirements.txt'.

### Bash

pip install -r requirements.txt


# Utilisation

Pour les données GPS il faut indiquer les valeurs sous la format " deg, min, sec ".
Pour le temps d'exposition et d'ouverture si rien n'est notée il faut les indiquer sour la format " num/denom ".
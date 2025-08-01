import os
import shutil

#Nakopíruje obrázky ze static/images/album-covers do media/album_covers
#spuštění pomocí python copy_covers.py

# Cesty (relativní k rootu Django projektu)
STATIC_DIR = 'static/images/album_covers'
MEDIA_DIR = 'media/album_covers'

os.makedirs(MEDIA_DIR, exist_ok=True)

# Projdi všechny soubory v source
for filename in os.listdir(STATIC_DIR):
    source_file = os.path.join(STATIC_DIR, filename)
    target_file = os.path.join(MEDIA_DIR, filename)

    # Zkopíruj jen soubory (vynech složky)
    if os.path.isfile(source_file):
        shutil.copy2(source_file, target_file)
        print(f'Zkopírováno: {filename}')

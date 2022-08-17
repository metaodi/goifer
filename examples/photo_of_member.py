import goifer
import os
from pprint import pprint
import requests

client = goifer.Client("canton_zurich")
member = client.search(
    index="Mitglieder",
    query='Wahlkreis adj "IX Horgen" and dauer_start > "2019-11-19 00:00:00"',
)

member = member[0]
pprint(member)

# download image

foto_id = member["foto_id"]
version = member["foto_version"]["nr"]
view = member["foto_version"]["rendition"][0]["ansicht"]
ext = member["foto_version"]["rendition"][0]["extension"]

download_path = os.path.join(".", f"foto.{ext}")
download_url = client.file("Mitglieder", foto_id, version, view)

r = requests.get(download_url)
print(f"Download file {download_url}...")
with open(download_path, "wb") as f:
    for chunk in r.iter_content(1024):
        f.write(chunk)

try:
    from PIL import Image

    img = Image.open(download_path)
    img.show()
except ImportError:
    print(f"Pillow is not installed, to view the photo, open '{download_path}'")

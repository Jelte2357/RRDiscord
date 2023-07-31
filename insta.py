from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
from instagrapi.types import Usertag, Location
import findcover
import requests
from PIL import Image
import os
    
def post(MusicName, MusicArtist, Tag):
    global cl
    download_image(findcover.album_cover(MusicName, MusicArtist))
    image = Image.open("Cover.jpg")
    image = image.convert("RGB")
    new_image = image.resize((1080, 1080))
    new_image.save("Cover.jpg")

    with open("Credentials.txt", 'r') as file:
        Name = file.readline().strip()
        Password = file.readline().strip()
        
    cl = Client()
    cl.delay_range = [1, 3]
    cl.login(Name, Password)
    if Tag == None:
        Data = cl.photo_upload("Cover.jpg", f"Nummer van de maand: {MusicName} door {MusicArtist}")
    else:
        Tagged = cl.user_info_by_username(Tag)
        Data = cl.photo_upload("Cover.jpg", f"Nummer van de maand: {MusicName} door {MusicArtist}", usertags=[Usertag(user=Tagged, x=0.5, y=0.5)])
    link = f"https://www.instagram.com/p/{Data.code}/"
    os.remove("Cover.jpg")
    cl.logout()
    return link

    
def download_image(url, file_path="Cover.jpg"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx errors

        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f"Image downloaded successfully: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")

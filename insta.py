from instagrapi import Client
from instagrapi.types import Usertag, Location
import findcover
import requests
from PIL import Image
from io import BytesIO
import pyotp
    
def post(MusicName, MusicArtist, Tag):
    global cl
    response = requests.get(findcover.album_cover(MusicName, MusicArtist))
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    image = image.convert("RGB")
    new_image = image.resize((1080, 1080))
    
    image_bytes = BytesIO()
    new_image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)


    with open("Credentials.txt", 'r') as file:
        Name = file.readline().strip()
        Password = file.readline().strip()

        
    cl = Client()
    cl.delay_range = [1, 3]
    try:
        totp = pyotp.TOTP("2KC7NNWKS6K2PWA2FW6MIKCHI644SY3N")
        verification_code = totp.now() 
    
        cl.login(Name, Password, verification_code=verification_code)
    except Exception as e:
        print(e)
        try:
            sessionid = "44132042602%3A41kQW6JNFUVgVn%3A7%3AAYerX5VbgIrBDUOyHTNTz-axGi1fo7Pt8Ua4Cgr10w"
            cl.login_by_sessionid(sessionid)
        except:
            print(e)
            return "Error"
    try:
        if Tag == None:
            Data = cl.photo_upload(image_bytes.getvalue(), f"Nummer van de maand: {MusicName.title()} door {MusicArtist.title()}")
        else:
            Tagged = cl.user_info_by_username(Tag)
            Data = cl.photo_upload(image_bytes.getvalue(), f"Nummer van de maand: {MusicName.title()} door {MusicArtist.title()}", usertags=[Usertag(user=Tagged, x=0.5, y=0.5)])
        link = f"https://www.instagram.com/p/{Data.code}/"
        cl.logout()
        return link
    except:
        return "Error"

from instagrapi import Client
from instagrapi.types import Usertag
import pyotp
    
    
# Post the image to Instagram from title and artist or image link (with tite and artist), and tag optional
def post(image, caption, Tag=None):
    global cl
    image_bytes = image

    # Get the credentials, Name, Pass, TFA, SessId from the Credentials.txt file
    with open("Credentials.txt", 'r') as file:
        Name = file.readline().strip()
        Password = file.readline().strip()
        TFA = file.readline().strip()
        sessionid = file.readline().strip()

    # Login to Instagram using the credentials with tfa. if this fails, login with sessionid
    cl = Client()
    cl.delay_range = [1, 3]
    try:
        totp = pyotp.TOTP(TFA)
        verification_code = totp.now() 
    
        cl.login(Name, Password, verification_code=verification_code)
    except Exception as e:
        print(e)
        try:
            cl.login_by_sessionid(sessionid)
        except:
            print(e)
            return "LoginError"
    
    #upload the image to instagram with the title and artist as caption, and tag if given
    try:
        if Tag == None:
            Data = cl.photo_upload(image_bytes.getvalue(), caption)
        else:
            Tagged = cl.user_info_by_username(Tag)
            Data = cl.photo_upload(image_bytes.getvalue(), caption, usertags=[Usertag(user=Tagged, x=0.5, y=0.5)])
        link = f"https://www.instagram.com/p/{Data.code}/"
        cl.logout()
        return link
    except:
        return "UploadError"


import discord
import insta
import traceback
import requests
import sys
import asyncio
import threading
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from findcover import *
import time

TOKEN = 'MTExODA3Nzk1NDI0OTk4MTk3Mg.G7-_Ol.Uz7JqEaU20DhinEiL8qYuyz4Tth2S3a_dGeNC0'
global client
intents = discord.Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global main_loop
    main_loop = asyncio.get_event_loop()
    thread=threading.Thread(target=message_thread, args=(message,))
    thread.start()
    
    
@client.event
async def on_reaction_add(reaction, user):
    global main_loop
    main_loop = asyncio.get_event_loop()
    thread = threading.Thread(target=reaction_thread, args=(reaction, user))
    thread.start()
    
def reaction_thread(reaction, user):
    emoji = reaction.emoji

    if user.bot:
        return

    if emoji == "✅":
        send(reaction.message, "check")
        asyncio.run_coroutine_threadsafe(reaction.message.clear_reactions(), loop=main_loop)
        
    elif emoji == "❌":
        send(reaction.message, "cross")
        asyncio.run_coroutine_threadsafe(reaction.message.clear_reactions(), loop=main_loop)


def message_thread(message):
    if message.author.bot or not message.guild:
        return
    
    if not ((message.channel.id == 1131575697530441758) or (message.channel.name == "commands")):
        return
    
    if (not message.content.startswith("!")) or message.content.startswith("! "):
        return
        
    if message.content == "!help":
        send(message, "Commands:")
        time.sleep(0.25)
        send(message, "!lightbar - nog niet geimplementeerd")
        time.sleep(0.25)
        send(message, "!insta - instagram upload (Gebruik !image, !insta is deprecated)")
        time.sleep(0.25)
        send(message, "!image - maakt nummer van de maand van een foto of naam en artiest")
        time.sleep(0.25)
        send(message, "gebruik '!{command} help' voor help per command")

        
    if message.content.startswith("!gay"):
        if message.author.global_name != "Jelte2357":
            send(message, f"{message.author.global_name} is zeer gay")
        else:
            send(message, f"{message.author.global_name} is niet gay")

    if message.content.startswith("!lightbar"):
        if "!lightbar help" in message.content:
            send(message, "nog niet geimplementeerd")
        cmd = message.content.split(' ', 1)[-1]
        
    if message.content.startswith("!image"):
        if message.content.startswith("!image help"):
            send(message, "gebruik:")
            time.sleep(0.25)
            send(message, "!image help - Laat dit zien")
            time.sleep(0.25)
            send(message, "!image n: titel a: artiest - maakt nummer van de maand van een naam en artiest")
            time.sleep(0.25)
            send(message, "!image n: titel a: artiest - UPLOAD ZELF EEN FOTO ERBIJ - maakt nummer van de maand van een foto")
            return
        
        send(message, "Dit kan even duren")
        if (len(message.attachments) >= 1) and (message.attachments[0].url.endswith((".png", ".jpg", ".jpeg"))):
            if len(message.content.split(' ')) < 2:
                send(message, "Ik mis een naam of een artiest bij deze foto, maar toch convert ik hem")
                image_bytes, output_file = cover_to_image(message, message.attachments[0].url, "overlay.png")
                image_file = discord.File(image_bytes, filename=output_file)
                
                if image_file:
                    sendRaw(message, file=image_file)
                else:
                    send(message, "Iets ging fout, maar ik weet zo niet wat")
            else:
                title, artist, tags = parse_post(message.content)
                if not (title and artist):
                    send(message, "Je hebt wel een foto, maar geen naam of artiest")
                    return
                image_bytes, output_file = cover_to_image(message, message.attachments[0].url, "overlay.png")
                image_bytes, output_file = text_overlay({"Title": title, "Font": "Helvetica.ttf", "Size": 144, "Color": (245,247,196), "pos": (62,1530)}, {"Artist": artist, "Font": "Helvetica.ttf", "Size": 96, "Color": (249,250,226), "pos": (62,1690)}, image_bytes, output_file)
                
                image_file = discord.File(image_bytes, filename=output_file)

                # text overlay
                if image_file:
                    sendRaw(message, file=image_file)
                else:
                    send(message, "Iets ging fout, maar ik weet zo niet wat")
            
        elif len(message.content.split(' '))>=2:
            name, artist, tags = parse_post(message.content)
            if not (name and artist):
                send(message, "geen nummer of artiest")
                return
            image_link = album_cover(name, artist)
            if not image_link:
                send(message, "invalide nummer of artiest, mogelijk typefout")
                return
                
            image_bytes, output_file = cover_to_image(message, image_link, "overlay.png")
            image_bytes, output_file = text_overlay({"Title": name, "Font": "Helvetica.ttf", "Size": 144, "Color": (245,247,196), "pos": (62,1530)}, {"Artist": artist, "Font": "Helvetica.ttf", "Size": 96, "Color": (249,250,226), "pos": (62,1690)}, image_bytes, output_file)
            
            image_file = discord.File(image_bytes, filename=output_file)
            
            if image_file:
                sendRaw(message, file=image_file)
            else:
                send(message, "Iets ging fout, maar ik weet zo niet wat")
        else:
            send(message, "Ik mis een foto, of muziek info")
        
            

    if message.content.startswith("!insta"): #Instagram Api
        if message.content == ("!insta help") or message.content == ("!insta"):
            send(message, "GEBRUIK DIT NIET MEER, gebruik '!image'")
            time.sleep(0.25)
            send(message, "gebruik:")
            time.sleep(0.25)
            send(message, "!insta help - Laat dit zien")
            time.sleep(0.25)
            send(message, "!insta post n: {nummer} a: {artiest} t: {intatag artiest} - (t: optioneel)")
            time.sleep(0.25)
            send(message, "!insta login {Naam} {Wachtwoord} - slaat voor altijd op.")
        
        if message.content.startswith("!insta login "):
            cmd = message.content.split(" ")
            try:
                write_credentials(cmd[2], cmd[3])
                send(message, f"Naam: {cmd[2]} Wachtwoord: {cmd[3]}")
                return
            except:
                send(message, "Kon wachtwoord niet veranderen, mogelijk mist er data")
                return
        if message.content.startswith("!insta post "):
            send(message, "Deze actie kan wat tijd kosten, heb geduld.")
            name, artist, tags = parse_post(message.content)
            if name == None or artist == None:
                send(message, "Ik mis een naam of een artiest")
                return
            if tags and tags.startswith("@"):
                tags=tags[1:]
                tags=tags.title()
            name, artist = name.title(), artist.title()
            try:
                link = insta.post(name, artist, tags)
                if link == "Error":
                    raise Exception("Te vaak geprobeerd in te loggen?, probeer later opnieuw? (ik weet het ook niet zeker)")
            except Exception as e:
                formatted_exception=format_exception(e)
                sendcrash(formatted_exception)
                send(message, f"Er ging iets fout, kijk in #Crashlog")
                if "No such file or directory: 'Cover.jpg'" in formatted_exception:
                    send(message, "Er kon geen cover worden gevonden (heb je de titel en artiest goed getyped)")
                    return
                elif ('{"message":"login_required","status":"fail"}' in formatted_exception) or ("Please wait a few minutes before you try again." in formatted_exception):
                    send(message, "Loging ging fout (mogelijk 2 post tegelijkertijd proberen te maken), probeer later opnieuw")
                    return
                else:
                    send(message, "Kon niet inloggen (te vaak op een dag geprobeerd?)")
                    return

            send(message, f"Succesvol gepost op Instagam: {link}")

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str

def write_credentials(name, password):
    with open("Credentials.txt", 'w') as file:
        file.write(name + '\n')
        file.write(password + '\n')
        
def parse_post(command):
    # Find the indices of 'n:', 'a:', and 't:', if they exist
    n_index = command.find('n:')
    a_index = command.find('a:')
    t_index = command.find('t:')

    # Extract the data based on the indices
    name = command[n_index + 2 : a_index].strip() if n_index != -1 else None
    artist = command[a_index + 2 : t_index if t_index != -1 else None].strip() if a_index != -1 else None
    tags = command[t_index + 2 :].strip() if t_index != -1 else None

    return name, artist, tags

def cover_to_image(message, url, overlay_file="overlay.png", output_file="AlbumCover.png"):
    response = requests.get(url)
    if not response.ok:
        send(message, "Kon de foto niet verwerken (downloaden mislukt)")
        return
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    overlay = Image.open(overlay_file)
    x,y = image.size
    
    if x!=y:
        send(message, "waarschijnlijk geen albumcover (geen vierkant)")
    
    image = image.resize(overlay.size)
    overlayed_image = Image.alpha_composite(image.convert("RGBA"), overlay.convert("RGBA"))
    image_bytes = BytesIO()
    overlayed_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    
    return image_bytes, output_file


def text_overlay(title, artist, image_bytes, output_file="AlbumCoverTO.png"):
    #title =  {"Title": "-Title-", "Font": "-FontPath.ttf-", "Size": Num, "Color": (R,G,B), pos: (x,y)}
    #artist = {"Artist": "-Artist-", "Font": "-FontPath.ttf-", "Size": "-Size-", "Color": (R,G,B), pos: (x,y)}
    image_data = image_bytes
    image = Image.open(image_data)
    
    #TITLE
    draw = ImageDraw.Draw(image)
    font_size = title["Size"]
    font = ImageFont.truetype(title["Font"], font_size)
    text = title["Title"].title()
    position = title["pos"]
    text_color = title["Color"]
    draw.text(position, text, font=font, fill=text_color)
    
    #ARTIST
    font_size = artist["Size"]
    font = ImageFont.truetype(artist["Font"], font_size)
    text = artist["Artist"].title()
    position = artist["pos"]
    text_color = artist["Color"]
    draw.text(position, text, font=font, fill=text_color)
    
    edited_image = image
    image_bytes = BytesIO()
    edited_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return image_bytes, output_file
    
def send(message, data, with_check=False):
    server = client.get_guild(message.guild.id)
    channel = discord.utils.get(server.channels, id=message.channel.id)

    fut = asyncio.run_coroutine_threadsafe(channel.send(data), loop=main_loop)
    
    if with_check:
        res = fut.result(timeout=5)
        fut2 = asyncio.run_coroutine_threadsafe(res.add_reaction('✅'), loop=main_loop)
        fut2.result(timeout=5)
        fut3 = asyncio.run_coroutine_threadsafe(res.add_reaction('❌'), loop=main_loop)
        fut3.result(timeout=5)
    
def sendRaw(message, *args, **kwargs):
    server = client.get_guild(message.guild.id)
    channel = discord.utils.get(server.channels, id=message.channel.id)

    asyncio.run_coroutine_threadsafe(channel.send(*args, **kwargs), loop=main_loop)

def sendcrash(data):
    print(data)
    server = client.get_guild(1118080988770213888)
    channel = discord.utils.get(server.channels, id=1131660567803858975)
    
    asyncio.run_coroutine_threadsafe(channel.send(data), loop=main_loop)

client.run(TOKEN)


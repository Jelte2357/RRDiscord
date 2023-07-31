import discord
import insta
import traceback
import sys
import asyncio
import threading

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

def message_thread(message):
    if message.author.bot or not message.guild:
        return
    
    if not ((message.channel.id == 1131575697530441758) or (message.channel.name == "commands")):
        return
    
    if (not message.content.startswith("!")) or message.content.startswith("! "):
        return

    if message.content == "!help":
        send(message, "Commands:")
        send(message, "!insta")
        send(message, "gebruik '!{command} help' voor help per command")

        
    if message.content.startswith("!gay"):
        if message.author.global_name != "Jelte2357":
            send(message, f"{message.author.global_name} is zeer gay")
        else:
            send(message, f"{message.author.global_name} is niet gay")

    if message.content.startswith("!lightbar"):
        cmd = message.content.split(' ', 1)[-1]

    if message.content.startswith("!insta"): #Instagram Api
        if message.content == ("!insta help") or message.content == ("!insta"):
            send(message, "gebruik:")
            send(message, "!insta help - Laat dit zien")
            send(message, "!insta post n: {nummer} a: {artiest} t: {intatag artiest} - (t: optioneel)")
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
            name, artist, tags = parse_insta_post(message.content)
            if name == None or artist == None:
                send(message, "Ik mis een naam of een artiest")
                return
            if tags and tags.startswith("@"):
                tags=tags[1:]
                tags=tags.title()
            name, artist = name.title(), artist.title()
            try:
                link = insta.post(name, artist, tags)
            except Exception as e:
                formatted_exception=format_exception(e)
                if "No such file or directory: 'Cover.jpg'" in formatted_exception:
                    send(message, "Er kon geen cover worden gevonden (heb je de titel en artiest goed getyped)")
                    return
                if ('{"message":"login_required","status":"fail"}' in formatted_exception) or ("Please wait a few minutes before you try again." in formatted_exception):
                    send(message, "Loging ging fout (mogelijk 2 post tegelijkertijd proberen te maken), probeer later opnieuw")
                    return
                sendcrash(formatted_exception)
                send(message, f"Er ging iets fout, kijk in #Crashlog")
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
        
def parse_insta_post(command):
    # Find the indices of 'n:', 'a:', and 't:', if they exist
    n_index = command.find('n:')
    a_index = command.find('a:')
    t_index = command.find('t:')

    # Extract the data based on the indices
    name = command[n_index + 2 : a_index].strip() if n_index != -1 else None
    artist = command[a_index + 2 : t_index if t_index != -1 else None].strip() if a_index != -1 else None
    tags = command[t_index + 2 :].strip() if t_index != -1 else None

    return name, artist, tags


def send(message, data):
    server = client.get_guild(message.guild.id)
    channel = discord.utils.get(server.channels, id=message.channel.id)

    asyncio.run_coroutine_threadsafe(channel.send(data), loop=main_loop)

def sendcrash(data):
    server = client.get_guild(1118080988770213888)
    channel = discord.utils.get(server.channels, id=1131660567803858975)
    
    asyncio.run_coroutine_threadsafe(channel.send(data), loop=main_loop)

client.run(TOKEN)


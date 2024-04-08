# To Do: /Lightbar (will add at a later date)
import discord
import insta
import requests
import asyncio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from findcover import album_cover
from typing import Literal, Optional
import os

if not os.path.exists("TOKEN"):
    print("Please enter the bot token in the file named 'TOKEN'")
    exit()
    
with open("TOKEN", "r") as file:
    TOKEN = file.read()
    
if TOKEN == "":
    print("Please enter the bot token in the file named 'TOKEN'")
    exit()

global client
intents = discord.Intents.all()
intents.message_content = True

class DiscordClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.synced = False
        self.added = False
        self.tree = discord.app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.playing, name="Muziek bij Radio Rijks")

    async def on_ready(self):
        await self.wait_until_ready()
        print("Syncing")
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        if not self.added:
            self.added = True
        print(f"Synced, {self.user} is running!")

client = DiscordClient()

def cover_to_image(image_url: str, overlay: str, output_file: str = "AlbumCover.png"):
    response = requests.get(image_url)
    if not response.ok:
        return None, "Download failed"
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    overlay = Image.open(overlay)
    x, y = image.size
    if x != y:
        return None, "Size"
    image = image.resize(overlay.size)
    overlayed_image = Image.alpha_composite(image.convert("RGBA"), overlay.convert("RGBA"))
    image_bytes = BytesIO()
    overlayed_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return image_bytes, output_file

def text_overlay(name: dict, artist: dict, image_bytes: BytesIO, output_file: str = "AlbumCoverTO.png"):
    image_data = image_bytes
    image = Image.open(image_data)
    draw = ImageDraw.Draw(image)
    font_size = name["Size"]
    font = ImageFont.truetype(name["Font"], font_size)
    text = name["Title"].title()
    position = name["pos"]
    text_color = name["Color"]
    draw.text(position, text, font=font, fill=text_color)
    
    font_size = artist["Size"]
    font = ImageFont.truetype(artist["Font"], font_size)
    text = artist["Artist"].title()
    position = artist["pos"]
    text_color = artist["Color"]
    draw.text(position, text, font=font, fill=text_color)
    
    image = image.convert("RGB")
    image = image.resize((1080, 1080))
    
    edited_image = image
    image_bytes = BytesIO()
    edited_image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return image_bytes, output_file

def defer(func):
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        await interaction.response.defer()
        await func(interaction, *args, **kwargs)
    return wrapper

class Checks:
    """Checking decorators for the commands. Class based for easy use."""
    def admin_only(func):
        """Check if user has admin permissions"""
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(f"You don't have permission to use this command, {interaction.user.mention}")
                return
            await func(interaction, *args, **kwargs)
        return wrapper
    
    def commands_channel_only(func):
        """Check if the command is used in the main channel"""
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if not interaction.channel.name == "commands":
                await interaction.followup.send(f"You can't use this command here, {interaction.user.mention}")
                return
            await func(interaction, *args, **kwargs)
        return wrapper
    
    
def confirm(func):
    """Roughly based uppon the reaction from "Just a random coder" on:
    https://stackoverflow.com/questions/76299397/how-to-add-accept-deny-button-to-a-submission-bot-discord-py/76302606#76302606"
    
    This decorator adds a confirm and cancel button to the command, and only runs the command if the confirm button is pressed by the same user who used the command.
    Made for safety."""
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        
        iu = interaction.user
        b1 = discord.ui.Button(label='Ja', style=discord.ButtonStyle.success)
        b2 = discord.ui.Button(label='Nee', style=discord.ButtonStyle.danger)
        view = discord.ui.View()
        view.add_item(b1)
        view.add_item(b2)
        async def b1_callback(interaction:discord.Interaction):
            if interaction.user != iu:
                await interaction.response.send_message(f"{interaction.user.mention}You can't confirm this command, as it was run by {iu.mention}.", ephemeral=True)
                return
            await prevmessage.edit(content="Bevestigd", view=None)
            await func(interaction, *args, **kwargs)
        async def b2_callback(interaction:discord.Interaction):
            if interaction.user != iu:
                await interaction.response.send_message(f"{interaction.user.mention}You can't cancel this command, as it was run by {iu.mention}.", ephemeral=True)
                return
            await prevmessage.edit(content="Geannuleerd", view=None)
        b1.callback = b1_callback
        b2.callback = b2_callback
        # sadly, this can NOT be set to only visible for the user who used the command (due to deferring), so we have to check if the user is the same as the user who used the command.
        prevmessage = await interaction.followup.send('Weet je het zeker?', ephemeral=True, view=view)
           
    return wrapper

def confirm_upload_instagram(func):
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        iu = interaction.user
        b1 = discord.ui.Button(label='Jazeker', style=discord.ButtonStyle.success)
        b2 = discord.ui.Button(label='Nee', style=discord.ButtonStyle.danger)
        view = discord.ui.View()
        view.add_item(b1)
        view.add_item(b2)
        async def b1_callback(interaction:discord.Interaction):
            if interaction.user != iu:
                await interaction.response.send_message(f"{interaction.user.mention}You can't confirm this command, as it was run by {iu.mention}.", ephemeral=True)
                return
            await prevmessage.edit(content="Bevestigd - Dit kan even duren", view=None)
            await func(interaction, *args, **kwargs)
        async def b2_callback(interaction:discord.Interaction):
            if interaction.user != iu:
                await interaction.response.send_message(f"{interaction.user.mention}You can't cancel this command, as it was run by {iu.mention}.", ephemeral=True)
                return
            await prevmessage.edit(content="Geannuleerd", view=None)
        b1.callback = b1_callback
        b2.callback = b2_callback
        # set them to delete after 2 minutes
        prevmessage = await interaction.followup.send('Wil je deze foto uploaden?', ephemeral=True, view=view)
        
    return wrapper

@client.tree.command(
    name="help",
    description="Get help with the commands"
)
async def help(interaction: discord.Interaction):
    @defer
    @Checks.commands_channel_only
    async def run(interaction: discord.Interaction):
        await interaction.followup.send(\
"""Het help menu:
/Lightbar: Past de text van de lightbar aan (nog niet geïmplementeerd)
/InstaLogin: Login bij instagram, voor de bot
/InstaPostImage: Post een afbeelding (met tekst) naar Instagram
/InstaPostText: Post een tekst (met afbeelding van spotify albumcover) naar Instagram
/Clear: Maak de chat leeg
/Help: Laat dit menu zien"""
)
    await run(interaction)
    
@client.tree.command(
    name="instalogin",
    description="Login to Instagram, multiple ways",
)
async def insta_login(interaction: discord.Interaction, name: str, password: str, tfa: str, sessionid: str):
    @defer
    @Checks.admin_only
    @Checks.commands_channel_only
    @confirm
    @defer
    async def run(interaction: discord.Interaction, name: str, password: str, tfa: str, sessionid: str):
        with open("Credentials.txt", 'w') as file:
            file.write(name + '\n')
            file.write(password + '\n')
            file.write(tfa + '\n')
            file.write(sessionid + '\n')
    await run(interaction, name, password, tfa, sessionid)

@client.tree.command(
    name="clear",
    description="Clear the chat",
)
async def clear(interaction: discord.Interaction):
    @defer
    @Checks.admin_only
    @confirm
    @defer
    async def run(interaction: discord.Interaction):
        await interaction.channel.purge()
    await run(interaction)

@client.tree.command(
    name="instapostimage",
    description="Post to Instagram",
)
async def insta_post_image(interaction: discord.Interaction, image: discord.Attachment, type: Literal["Nummer van de maand", "New Music Friday"], nummer: str, artiest: str, caption: str, tag: Optional[str] = None):
    @defer
    #@Checks.admin_only
    @Checks.commands_channel_only
    async def run(interaction: discord.Interaction, image: discord.Attachment, type: Literal["Nummer van de maand", "New Music Friday"], nummer: str, artiest: str, caption: str):
        # check if the attachment is an image
        if not image.content_type.startswith("image"):
            await interaction.followup.send("Dit is geen afbeelding")
            return
        
        tag = tag.lstrip("@")
        
        if type == "Nummer van de maand":
            image_bytes, output_file = cover_to_image(image.url, "NVDM.png") 
        elif type == "New Music Friday":
            image_bytes, output_file = cover_to_image(image.url, "NMF.png")
        else:
            await interaction.followup.send("Er ging iets fout")
            return
                
        if image_bytes == None:
            await interaction.followup.send(f"Er ging iets fout. Dit betreft {output_file}")
            return
        image_bytes, output_file = text_overlay({"Title": nummer, "Font": "Helvetica.ttf", "Size": 144, "Color": (245,247,196), "pos": (62,1530)}, {"Artist": artiest, "Font": "Helvetica.ttf", "Size": 96, "Color": (249,250,226), "pos": (62,1690)}, image_bytes, output_file)
        
        interaction.followup.send("Dit is de foto", file=discord.File(image_bytes, filename=output_file))
        
        @confirm_upload_instagram
        async def confirm_upload(interaction: discord.Interaction):
           commands_channel = discord.utils.get(interaction.guild.text_channels, name="commands")
           loop = asyncio.get_running_loop()
           result = await loop.run_in_executor(None, insta.post, image_bytes, caption, tag)
           await commands_channel.send(f"Foto geupload met link: {result}")
        await confirm_upload(interaction)
        
        
    await run(interaction, image, type, nummer, artiest, caption)
    
@client.tree.command(
    name="instaposttext",
    description="Post to Instagram",
)
async def insta_post_text(interaction: discord.Interaction, type: Literal["Nummer van de maand", "New Music Friday"], nummer: str, artiest: str, caption: str, tag: Optional[str] = None):
    @defer
    #@Checks.admin_only
    @Checks.commands_channel_only
    async def run(interaction: discord.Interaction, type: Literal["Nummer van de maand", "New Music Friday"], nummer: str, artiest: str, caption: str):
        image_link = album_cover(nummer, artiest)
        if not image_link:
            await interaction.followup.send("Invalide nummer of artiest, mogelijk typefout")
            return
        
        if type == "Nummer van de maand":
            image_bytes, output_file = cover_to_image(image_link, "NVDM.png")
        elif type == "New Music Friday":
            image_bytes, output_file = cover_to_image(image_link, "NMF.png")
        else:
            await interaction.followup.send("Er ging iets fout")
            return

        if image_bytes == None:
            await interaction.followup.send(f"Er ging iets fout. Dit betreft {output_file}")
            return
        image_bytes, output_file = text_overlay({"Title": nummer, "Font": "Helvetica.ttf", "Size": 144, "Color": (245,247,196), "pos": (62,1530)}, {"Artist": artiest, "Font": "Helvetica.ttf", "Size": 96, "Color": (249,250,226), "pos": (62,1690)}, image_bytes, output_file)
        
        await interaction.followup.send("Dit is de foto", file=discord.File(image_bytes, filename=output_file))
        
        @confirm_upload_instagram
        async def confirm_upload(interaction: discord.Interaction):
           commands_channel = discord.utils.get(interaction.guild.text_channels, name="commands")
           loop = asyncio.get_running_loop()
           result = await loop.run_in_executor(None, insta.post, image_bytes, caption, tag)
           await commands_channel.send(f"Foto geupload met link: {result}")
        await confirm_upload(interaction)
   
    await run(interaction, type, nummer, artiest, caption)
    
client.run(TOKEN)
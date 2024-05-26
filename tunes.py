import discord
import os
import asyncio 
import yt_dlp
from dotenv import load_dotenv

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now listening to some tunes')

    @client.event
    async def on_message(message): 
        if message.author == client.user:
            return

        if message.content.startswith("/play"): 
            if message.author.voice and message.author.voice.channel:
                voice_channel = message.author.voice.channel
                try:
                    voice_client = await voice_channel.connect()
                    voice_clients[voice_client.guild.id] = voice_client
                    await message.channel.send(f"Connected to {voice_channel}")
                except discord.errors.ClientException as e:
                    await message.channel.send(f"Error connecting to the voice channel: {str(e)}")
                except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")
                
                try:
                    url = message.content.split()[1]
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                    song = data['url']
                    audio_source = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                    voice_clients[message.guild.id].play(audio_source)
                except discord.errors.ClientException as e:
                    await message.channel.send(f"Error connecting to the voice channel: {str(e)}")
                except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")
            else:
                await message.channel.send("You need to be in a voice channel to use the /play command.")

        if message.content.startswith("/pause"):
            try:
                voice_clients[message.guild.id].pause()
            except discord.errors.ClientException as e:
                    await message.channel.send(f"Error connecting to the voice channel: {str(e)}")
            except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")

        if message.content.startswith("/resume"):
            try:
                voice_clients[message.guild.id].resume()
            except discord.errors.ClientException as e:
                    await message.channel.send(f"Error connecting to the voice channel: {str(e)}")
            except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")

        if message.content.startswith("/stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except discord.errors.ClientException as e:
                    await message.channel.send(f"Error connecting to the voice channel: {str(e)}")
            except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")

    client.run(TOKEN)
import discord
from discord.ext import commands
import asyncio
from MusicaBot.buscar import search_youtube
from MusicaBot.audio import get_youtube_audio_url
from youtube_search import YoutubeSearch
import os
from dotenv import load_dotenv
import json

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents().all())
        self.voice_client = None
        self.music_queue = []  # Cola para almacenar las URLs de música
        self.is_playing = False  # Indicador de estado de reproducción

    async def play_music(self, user_id, channel_id, guild_id, query):
        try:
            print(f"Buscando audio para la consulta: {query}")
            guild = self.get_guild(int(guild_id))
            if guild is None:
                print("No se pudo encontrar el servidor.")
                return "El bot no está en el servidor especificado."
            
            member = guild.get_member(int(user_id))
            if member is None:
                print("El usuario no se encuentra en el servidor.")
                return "El usuario no se encuentra en el servidor."

            # Verifica si el usuario está en un canal de voz
            if member.voice is None or member.voice.channel.id != int(channel_id):
                print("El usuario no está en el canal de voz correcto.")
                return f"El usuario {user_id} no está en el canal de voz correcto."

            # Busca el audio de YouTube basado en la consulta
            extract = search_youtube(query)

            results = YoutubeSearch(extract, max_results=1).to_json()
            data_url = json.loads(results)

            url = get_youtube_audio_url(extract)

            if not url:
                raise ValueError("No se pudo obtener la URL del audio.")

            # Agrega la URL a la cola de música
            self.music_queue.append(url)
            print(f"Agregada a la cola: {url}. Cola actual: {self.music_queue}")

            # Si el bot no está reproduciendo, comienza a reproducir
            if self.voice_client is None:
                # Conectar al canal de voz
                self.voice_client = await member.voice.channel.connect()

            # Iniciar la reproducción si no hay música sonando
            if not self.is_playing:
                asyncio.create_task(self.start_playing())  # Reproducción en segundo plano

            # Enviar respuesta JSON inmediatamente
            return {"status": "success", "message": "Canción agregada a la cola", "queue": self.music_queue, "info_music": data_url}

        except Exception as e:
            print(f"Error al reproducir música: {e}")
            return {"status": "error", "message": str(e)}

    async def start_playing(self):
        # Maneja la reproducción de música en cola
        while self.music_queue:
            url = self.music_queue.pop(0)  # Obtiene la siguiente URL de la cola

            # Opciones de FFmpeg mejoradas
            ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn -loglevel panic'}

            self.is_playing = True
            # Reproducir el audio
            self.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=self.check_queue)

            # Espera hasta que termine la reproducción
            while self.voice_client.is_playing():
                await asyncio.sleep(1)

        # Desconectar después de que se haya terminado la cola
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        self.is_playing = False

    def check_queue(self, error=None):
        if error:
            print(f"Error en la reproducción: {error}")
        # Llama a start_playing para reproducir la siguiente canción en la cola
        if self.music_queue:
            asyncio.create_task(self.start_playing())

    async def show_queue(self):
        return self.music_queue  # Devuelve la cola actual

    async def stop_music(self, user_id, guild_id):
        guild = self.get_guild(int(guild_id))
        if not guild:
            return {"status": "error", "message": "Servidor não encontrado."}

        member = guild.get_member(int(user_id))
        if not member:
            return {"status": "error", "message": "Usuário não encontrado no servidor."}

        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.is_playing = False
            self.music_queue = []  # Limpa a fila de músicas
            return {"status": "success", "message": "Bot desconectado e fila de músicas limpa."}
        
        return {"status": "error", "message": "O bot não está em um canal de voz."}

    async def on_ready(self):
        print(f"Bot conectado como {self.user} en el servidor.")

    async def start_bot(self):
        # Inicia el bot
        TOKEN = os.getenv("DISCORD_TOKEN")
        await self.start(TOKEN)

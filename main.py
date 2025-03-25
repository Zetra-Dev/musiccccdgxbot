from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bot import MusicBot  # Importação do MusicBot
import asyncio
import os
from dotenv import load_dotenv
import uvicorn

app = FastAPI()

bots = {}  # Dicionário de bots baseado em tokens

# Inicializar o bot globalmente
music_bot = MusicBot()

class MusicRequest(BaseModel):
    token: str
    user_id: str
    channel_id: str
    guild_id: int
    query: str

# Restante das classes...

@app.on_event("startup")
async def startup_event():
    # Inicia o bot de Discord ao iniciar o servidor
    await music_bot.start_bot()  # Agora é await, garantido que o bot inicializa

@app.post("/play-music")
async def play_music(request: MusicRequest):
    try:
        m = await music_bot.play_music(request.user_id, request.channel_id, request.guild_id, request.query)
        return JSONResponse({"message": m}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pause-music")
async def pause_music(request: GuildRequest):
    if request.token in bots:
        return await bots[request.token].pause_music(request.guild_id)
    return {"status": 404, "message": "Bot não encontrado."}

# As outras rotas seguem o mesmo formato de verificação e execução

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

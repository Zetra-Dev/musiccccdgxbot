from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bot import MusicBot
import asyncio
import os
from dotenv import load_dotenv
import uvicorn

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()
music_bot = MusicBot()

class MusicRequest(BaseModel):
    user_id: str
    channel_id: str
    guild_id: str
    query: str

class GuildRequest(BaseModel):
    guild_id: str

@app.on_event("startup")
async def startup_event():
    # Inicia el bot de Discord
    asyncio.create_task(music_bot.start_bot())

@app.post("/play-music")
async def play_music(request: MusicRequest):
    try:
        m = await music_bot.play_music(request.user_id, request.channel_id, request.guild_id, request.query)
        return JSONResponse({"message": m}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pause-music")
async def pause_music(request: GuildRequest):
    try:
        m = await music_bot.pause_music(request.guild_id)
        return JSONResponse({"message": m}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/resume-music")
async def resume_music(request: GuildRequest):
    try:
        m = await music_bot.resume_music(request.guild_id)
        return JSONResponse({"message": m}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/skip-music")
async def skip_music(request: GuildRequest):
    try:
        m = await music_bot.skip_music(request.guild_id)
        return JSONResponse({"message": m}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/music-queue")
async def music_queue():
    try:
        queue = await music_bot.show_queue()
        return {"queue": queue}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    # Inicia la aplicación FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)

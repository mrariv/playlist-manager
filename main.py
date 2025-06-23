from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Table, Column, Integer, String, Boolean
from sqlalchemy import create_engine, MetaData
from sqlalchemy import insert, select, update, delete, func
import os
import pymysql
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

pymysql.install_as_MySQLdb()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:mysecretpassword@localhost:3306/playlist_db")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

songs_table = Table(
    "songs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("artist", String(100)),
    Column("title", String(100)),
    Column("genre", String(50)),
    Column("liked", Boolean, default=False), 
    Column("cover_url", String(5000), nullable=True)
)

app = FastAPI()

class Song(BaseModel):
    id: int | None = None
    artist: str
    title: str
    genre: str
    liked: bool = False
    cover_url: str | None = None

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
def web_ui():
    return RedirectResponse(url="/static/index.html")

@app.on_event("startup")
def startup():
    metadata.create_all(engine)

@app.get("/")
def root():
    return "Welcome to your playlist manager!"

@app.post("/songs")
def create_item(item: Song):
    query = insert(songs_table).values(
        artist = item.artist,
        title = item.title,
        genre = item.genre,
        liked = item.liked,
        cover_url = item.cover_url
    )
    with engine.begin() as conn:
        result = conn.execute(query)
        song_id = result.lastrowid
        new_song = conn.execute(select(songs_table).where(songs_table.c.id == song_id)).first()
    return Song(**dict(new_song._mapping))

@app.get("/songs", response_model=list[Song])
def list_songs(limit: int = 10):
    query = select(songs_table).limit(limit)
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
    return [Song(**dict(row._mapping)) for row in result]
    
@app.get("/songs/random", response_model=Song)
def get_random_song():
    query = select(songs_table).order_by(func.rand()).limit(1)
    with engine.connect() as conn:
        result = conn.execute(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="No songs available")
    return Song(**dict(result._mapping))

@app.get("/songs/filter", response_model=list[Song])
def filter_songs(genre: str = None, liked: bool = None):
    query = select(songs_table)
    if genre is not None:
        query = query.where(songs_table.c.genre.like(f"%{genre.lower()}%"))
    if liked is not None:
        query = query.where(songs_table.c.liked == liked)

    with engine.connect() as conn:
        result = conn.execute(query).fetchall()

    return [Song(**dict(song._mapping)) for song in result]

@app.get("/songs/{song_id}", response_model=Song)
def get_song(song_id: int) -> Song:
    query = select(songs_table).where(songs_table.c.id == song_id)
    with engine.connect() as conn:
        result = conn.execute(query).first()
    if not result:
        raise HTTPException(status_code=404, detail=f'Song {song_id} not found')
    return Song(**dict(result._mapping))

@app.delete("/songs/{song_id}")
def delete_song(song_id: int):
    query = delete(songs_table).where(songs_table.c.id == song_id)
    with engine.begin() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f'Song {song_id} not found')
    return {"message": f"Song {song_id} deleted"}


@app.patch("/songs/{song_id}/like")
def like_song(song_id: int):
    query = update(songs_table).where(songs_table.c.id == song_id).values(liked=True)
    with engine.begin() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f'Song {song_id} not found')
    
    query = select(songs_table).where(songs_table.c.id == song_id)
    with engine.connect() as conn:
        song = conn.execute(query).first()
    return Song(**dict(song._mapping))
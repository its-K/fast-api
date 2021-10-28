from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class User(BaseModel):
    username: str
    password: str

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('SUPER_SECRET')

class Movie(BaseModel):
    movie: str

class MovieAdd(BaseModel):
    name: str
    genre: str
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from data import Settings

app = FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()

def createToken(data,Authorize):
    access_token = Authorize.create_access_token(subject= data)
    return {"access_token": access_token}

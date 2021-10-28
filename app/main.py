from fastapi import FastAPI, Depends, Request, HTTPException
from starlette.responses import JSONResponse
from db import db
from auth.authHandler import AuthJWT,createToken
from fastapi_jwt_auth.exceptions import AuthJWTException
from data import User, Movie, MovieAdd
import bcrypt

app = FastAPI()
collection = db.connect_database()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.get("/movies")
async def getMovies(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    movies=collection['movies']
    results = []
    for res in movies.find():
        res.pop('_id',None)
        results.append(res)
    current_user = Authorize.get_jwt_subject()
    print(current_user)
    userDetails=collection['users'].find_one({"username" : current_user})
    for wmovies in userDetails['watchlist']:
        for movie in results:
            if wmovies==movie['name']:
                movie['watched']=True
    return results

@app.post("/addtowatchlist")
async def addtowatchlist(movie: Movie,Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    userDetails=collection['users'].find_one({'username':current_user})
    movies=userDetails['watchlist']
    for wmovie in movies:
        if movie.movie==wmovie:
            return {"status" : "Movie already in watchlist"}
    userDetails['watchlist'].append(movie.movie)
    collection['users'].update({'username':current_user},userDetails)
    return {"status" : "Movie added to watch list"}

@app.delete("/removefromwatchlist")
async def removefromwatchlist(movie: Movie,Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    userDetails=collection['users'].find_one({'username':current_user})
    movies=userDetails['watchlist']
    for wmovie in movies:
        if movie.movie==wmovie:
            userDetails['watchlist'].remove(movie.movie)
    collection['users'].update({'username':current_user},userDetails)
    return {"status" : "Movie removed from watchlist"}

@app.get("/mywatchlist")
async def getwatchlist(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    userDetails=collection['users'].find_one({'username':current_user})
    movies=userDetails['watchlist']
    return {"movies": movies}

@app.post("/addmovies")
async def addmovies(movie: MovieAdd, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    movies=collection['movies']
    movies.insert({'name': movie.name,'genre': movie.genre})
    return {"status":"New movie added"}

@app.post("/login")
async def login(user : User,Authorize: AuthJWT = Depends()):
    if len(user.username) <3 or len(user.password) <4:
        raise HTTPException(status_code=400, detail="Username/Password too small.")
    users=collection['users']
    userDetails=users.find_one({"username":user.username})
    if userDetails==None:
        raise HTTPException(status_code=404, detail="User not found")
    if bcrypt.checkpw(bytes(user.password, 'utf-8'), userDetails['password']):
        return createToken(user.username,Authorize)
    else:
        raise HTTPException(status_code=404, detail="Username/Password doesn't match")

@app.post("/signup")
async def signup(user : User, Authorize : AuthJWT = Depends()):
    if len(user.username)<3 and len(user.password)<4:
        raise HTTPException(status_code=400,detail="Username/Password too small.")
    users=collection['users']
    hashed_password = bcrypt.hashpw(bytes(user.password, 'utf-8'), bcrypt.gensalt())
    users.insert({"username":user.username, "password":hashed_password, "is_admin":False, "watchlist":[]})
    return createToken(user.username,Authorize)
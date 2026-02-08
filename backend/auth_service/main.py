from fastapi import FastAPI

from routers.auth import auth_router

app = FastAPI()

@app.get("/")
async def root():
    return {"detail": "all ready!"}


app.include_router(auth_router)
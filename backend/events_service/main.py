from fastapi import FastAPI

from routers.event import event_router

app = FastAPI()


@app.get("/")
async def root():
    return {"detail": "all ready"}


app.include_router(event_router)
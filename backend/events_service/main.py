from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers.attendee import application_router
from routers.event import event_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"detail": "all ready"}


app.include_router(event_router)
app.include_router(application_router)
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers.organizer import organizer_router
from routers.volunteer import volunteer_router

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
    return {"message": "all ready!"}


app.include_router(volunteer_router)
app.include_router(organizer_router)
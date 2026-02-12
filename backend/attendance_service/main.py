from fastapi import FastAPI

from routers.volunteer import volunteer_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "all ready!"}


app.include_router(volunteer_router)
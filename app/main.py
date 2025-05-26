import sys
from fastapi import FastAPI, APIRouter
from .routers import review

# print(sys.executable)


app = FastAPI()

app.include_router(review.router)


@app.get("/")
async def root():
    return {"message": "Hello Hello Hello Hello !"}

import sys
from fastapi import FastAPI
from routers import review

# print(sys.executable)

# create fastapi app
app = FastAPI()

# add routers
app.include_router(review.router)


# add root level endpoint
@app.get("/")
async def root():
    return {"message": "Hello Hello Hello Hello !"}

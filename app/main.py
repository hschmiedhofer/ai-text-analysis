from fastapi import FastAPI
from fastapi.security import HTTPBearer
from services.database import create_db_and_tables
from routers import review
from fastapi.responses import HTMLResponse


# create fastapi app
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# add routers
app.include_router(review.router)


# add root level endpoint
@app.get("/")
async def root():
    html_content = """
    <html>
        <head>
            <title>Hello</title>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

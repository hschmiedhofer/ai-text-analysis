from fastapi import APIRouter
from models.models import Editorial

router = APIRouter(
    prefix="/review", tags=["review"]
)  # todo add dependencies and responses


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def get_test_response():
    return fake_items_db


@router.post("/")
async def submit_editorial(editorial: Editorial):
    return f"submitted: {editorial.name}"

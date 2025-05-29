import select
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Field, SQLModel, select
from services.database import SessionDep


from http import HTTPStatus


router = APIRouter(prefix="/test", tags=["test"])  # todo add dependencies and responses


class TestEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int = Field(index=True)


@router.post("/")
def create_entry(name: str, age: int, session: SessionDep) -> TestEntry:
    entry = TestEntry(name=name, age=age)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.get("/")
def read_entries(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[TestEntry]:
    entries = session.exec(select(TestEntry).offset(offset).limit(limit)).all()
    entries = list(entries)
    return entries


@router.get("/{hero_id}")
def read_single_entry(entry_id: int, session: SessionDep) -> TestEntry:
    entry = session.get(TestEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

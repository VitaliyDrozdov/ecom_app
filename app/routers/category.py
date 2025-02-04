from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from slugify import slugify
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Category
from app.schemas import CreateCategory

router = APIRouter(prefix="/categories", tags=["Category"])


@router.get("/")
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(
        select(Category).where(Category.is_active == True)
    )
    return categories.all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_category: CreateCategory,
):
    await db.execute(
        insert(Category).values(
            name=create_category.name,
            parent_id=create_category.parent_id,
            slug=slugify(create_category.name),
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Sucessful"}


@router.put("/")
async def update_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int,
    update_category: CreateCategory,
):
    category = await db.scalar(
        select(Category).where(Category.id == category_id)
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    category.name = update_category.name
    category.slug = slugify(update_category.name)
    category.parent_id = update_category.parent_id
    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Category update succeded",
    }


@router.delete("/")
async def delete_category(
    db: Annotated[AsyncSession, Depends(get_db)], category_id: int
):
    category = await db.scalar(
        select(Category).where(Category.id == category_id)
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    category.is_active = False
    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Category deleted",
    }

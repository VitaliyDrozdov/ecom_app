from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from slugify import slugify
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Category, Product
from app.schemas import CreateProduct

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product).where(Product.is_active == True, Product.stock > 0)
    )
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are not products",
        )
    return products.all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct
):
    category = await db.scalar(
        select(Category).where(Category.id == create_product.category)
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    await db.execute(
        insert(Product).values(
            name=create_product.name,
            price=create_product.price,
            image_url=create_product.image_url,
            slug=slugify(create_product.name),
            stock=create_product.stock,
            description=create_product.description,
            category_id=create_product.category,
            rating=0.0,
        )
    )
    await db.commit()
    return {
        "status_codes": status.HTTP_201_CREATED,
        "transaction": "Sucessful",
    }


@router.get("/{category_slug}")
async def product_by_category(
    category_slug: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    category = await db.scalar(
        select(Category).where(Category.slug == category_slug)
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_slug} not found",
        )
    subcategories = await db.scalars(
        select(Category).where(Category.parent_id == category.id)
    )
    all_categories_ids = list()
    if subcategories:
        all_categories_ids.extend([cat.id for cat in subcategories.all()])
    all_categories_ids.append(category.id)
    res = await db.scalars(
        select(Product).where(
            Product.category_id.in_(all_categories_ids),
            Product.is_active == True,
            Product.stock > 0,
        )
    )
    return res.all()


@router.get("/detail/{product_slug}")
async def product_detail(
    product_slug: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    product = await db.scalar(
        select(Product).where(
            Product.slug == product_slug,
            Product.is_active == True,
            Product.stock > 0,
        )
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There are not product with slug {product_slug}",
        )
    return product


@router.put("/{product_slug}")
async def update_product(
    product_slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    update_product: CreateProduct,
):
    category = await db.scalar(
        select(Category).where(Category.id == update_product.category)
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no category id {update_product.category} found",
        )
    product = await db.scalar(
        select(Product).where(Product.slug == product_slug)
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no product with slug {product_slug}",
        )
    product.name == update_product.name
    product.description = update_product.description
    product.price = update_product.price
    product.image_url = update_product.image_url
    product.stock = update_product.stock
    product.category_id = update_product.category
    product.slug = slugify(update_product.name)

    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": f"Product {product_slug} updated",
    }


@router.delete("/{product_slug}")
async def delete_product(
    product_slug: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.scalar(
        select(Product).where(Product.slug == product_slug)
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no product with slug {product_slug} not found",
        )
    result.is_active == False
    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product deleted",
    }

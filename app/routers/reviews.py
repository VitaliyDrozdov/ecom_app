from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Product, Rating, Review
from app.routers.permissions import role_required
from app.schemas import CreateRating, CreateReview

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=List[CreateReview])
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    # if not reviews:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="There are no reviews found",
    #     )
    return reviews.all()


@router.get("/{product_slug}/", response_model=List[CreateReview])
async def product_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()],
):
    product = await db.scalar(
        select(Product).where(
            Product.slug == product_slug, Product.is_active == True
        ),
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"""Product with slug {product_slug}
            not found or product.is_active==False""",
        )
    reviews = await db.scalars(
        select(Review).where(
            Review.is_active == True, Review.product_id == product.id
        )
    )
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No reviews found for product {product_slug}",
        )

    return reviews.all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_review: CreateReview,
    create_rating: CreateRating,
    cur_user: Annotated[
        dict, Depends(role_required(["is_admin", "is_customer"]))
    ],
):
    try:
        await db.execute(
            insert(Review).values(
                user_id=cur_user.get("id"),
                product_id=create_review.product,
                rating_id=create_review.rating,
                comment=create_review.comment,
            )
        )
        await db.execute(
            insert(Rating).values(
                grade=create_rating.grade,
                user_id=create_rating.user,
                product_id=create_rating.product,
            )
        )
        await db.commit()
        ratings = await db.scalars(
            select(Rating).where(
                Rating.product_id == create_rating.product,
                Rating.is_active == True,
            ),
        )

        new_rating = sum(r.grade for r in ratings) / len(ratings)
        product = await db.scalar(
            select(Product).where(Product.id == create_review.product)
        )
        product.rating = new_rating
        await db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"error:\n {e}"
        )


@router.delete("/{product_slug}/{review_id}")
async def delete_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    cur_user: Annotated[dict, Depends(role_required(["is_admin"]))],
    # cur_review: CreateReview,
    # cur_rating: CreateRating,
    # product_slug: str,
    review_id: int,
):
    review = await db.scalar(
        select(Review).where(Review.id == review_id, Review.is_active == True)
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no reviw found",
        )
    review.is_active = False
    await db.commit()
    # Опционально, можете обновить рейтинг товара, если необходимо
    # product = await db.scalar(
    #     select(Product).where(Product.id == review.product_id)
    # )
    # ratings = await db.scalars(
    #     select(Rating).where(
    #         Rating.product_id == product.id, Rating.is_active == True
    #     )
    # )
    # new_rating = sum(r.grade for r in ratings) / len(ratings)
    # if ratings else 0
    # product.rating = new_rating
    # await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Review deleted successfully",
    }

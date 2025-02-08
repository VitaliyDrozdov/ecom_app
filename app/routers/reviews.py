from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import exists, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.backend.db_depends import get_db
from app.models import Product, Rating, Review
from app.routers.permissions import role_required
from app.schemas import CreateReview

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/")
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(
        select(Review)
        .options(selectinload(Review.rating).load_only(Rating.grade))
        .where(Review.is_active == True)
    )
    reviews_res = reviews.all()
    if not reviews_res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no reviews found",
        )
    return reviews_res


@router.get("/{product_slug}/")
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
    reviews_all = reviews.all()
    if not reviews_all:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No reviews found for product {product_slug}",
        )

    return reviews_all


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_review: CreateReview,
    cur_user: Annotated[dict, Depends(role_required(["is_customer"]))],
):
    async with db.begin():
        try:
            user_id = cur_user.get("id")
            product_id = create_review.product_id
            check_review_exists = await db.scalar(
                select(
                    exists().where(
                        Review.user_id == user_id,
                        Review.product_id == product_id,
                    )
                )
            )
            if check_review_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already submitted a review for this product",
                )
            new_rating_obj = Rating(
                grade=create_review.grade,
                user_id=user_id,
                product_id=product_id,
            )
            new_review_obj = Review(
                user_id=user_id,
                comment=create_review.comment,
                product_id=product_id,
                rating=new_rating_obj,
            )
            db.add(new_review_obj)
            # await db.commit()
            # await db.refresh(new_review_obj)
            avg_rating = await db.scalar(
                select(func.avg(Rating.grade)).where(
                    Rating.product_id == product_id, Rating.is_active == True
                )
            )
            if avg_rating is not None:
                await db.execute(
                    update(Product)
                    .where(Product.id == product_id)
                    .values(rating=avg_rating)
                )
                # Вариант 2 (выбираются все модели Rating). Могу быть проблемы
                # с памятью, когда очень много записей рейтингов для товара.
                # ratings = await db.scalars(d
                #     select(Rating).where(
                #         Rating.product_id == create_review.product_id,
                #         Rating.is_active == True,
                #     ),
                # )
                # ratings_all = ratings.all()
                # if ratings_all:
                #     avg_rating = sum(r.grade for r in ratings_all) /
                # len(ratings_all)
                #     product_obj = await db.scalar(
                #         select(Product).where(
                # Product.id == create_review.product_id)
                #     )
                #     product_obj.rating = avg_rating
                # await db.commit()
                return {
                    "status_code": status.HTTP_201_CREATED,
                    "transaction": "Successful",
                }
        except SQLAlchemyError as e:
            # await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"error:\n {e}"
            )


@router.delete("/{product_slug}/{review_id}")
async def delete_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    cur_user: Annotated[dict, Depends(role_required(["is_admin"]))],
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

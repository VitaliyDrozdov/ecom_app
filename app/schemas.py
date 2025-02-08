from pydantic import BaseModel, field_validator


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class CreateReview(BaseModel):
    product_id: int
    comment: str
    grade: float

    @field_validator("grade")
    def check_grade(cls, value):
        if not 1 <= value <= 10:
            raise ValueError("Grade must be beteen 1-10")
        return value


# class ReviewResponse(BaseModel):
#     comment: str
#     product_id: int
#     grade: float

#     @classmethod
#     def from_orm(cls, review: Review):
#         return cls(
#             product_id=review.product_id,
#             comment=review.comment,
#             grade=review.rating.grade if review.rating else 0.0,
#         )

#     class Config:
#         from_attributes = True


# class CreateReview(BaseModel):
#     product_id: int
#     rating: int
#     comment: str


# class CreateRating(BaseModel):
#     grade: float
#     product_id: int

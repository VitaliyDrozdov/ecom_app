# isort:skip_file
import datetime as dt

from sqlalchemy.orm import relationship

from app.backend.db import Base

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating_id = Column(Integer, ForeignKey("ratings.id"), nullable=False)
    comment = Column(Text, nullable=False)
    comment_date = Column(
        DateTime, default=lambda: dt.datetime.now(dt.timezone.utc)
    )
    is_active = Column(Boolean, default=True)

    user = relationship("User", backref="reviews")
    product = relationship("Product", backref="reviews")
    rating = relationship("Rating", back_populates="review", uselist=False)


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Float, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    is_active = Column(Boolean, default=True)

    user = relationship("User", backref="ratings")
    product = relationship("Product", backref="ratings")
    review = relationship("Review", back_populates="rating", uselist=False)

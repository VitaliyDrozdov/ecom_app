from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/permissions", tags=["Persmissions"])


@router.patch("/")
async def supplier_permission(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    user_id: int,
):
    if get_user.get("is_admin"):
        user = await db.scalar(select(User).where(User.id == user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # TODO: refactor(вынести в отдельную функцию)
        if user.is_supplier:
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_supplier=False, is_customer=True)
            )
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "User is no longer supplier",
            }
        else:
            # TODO: refactor(вынести в отдельную функцию)
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_supplier=True, is_customer=False)
            )
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "User is now supplier",
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
        )


@router.delete("/delete")
async def delete_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    user_id: int,
):
    if get_user.get("is_admin"):
        user = await db.scalar(select(User).where(User.id == user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete admin user",
            )

        if user.is_active:
            await db.execute(
                update(User).where(User.id == user_id).values(is_active=False)
            )
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "User is deleted",
            }
        else:
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "User has already been deleted",
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permission",
        )


def role_required(allowed_roles: List[str]):
    def check_role(get_user: Annotated[dict, Depends(get_current_user)]):

        if not any(get_user.get(role, False) for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource",
            )
        return get_user

    return check_role


# TODO: refactor. Можно заменить во всех местах проверку админа,
# на новую зависимость.
# async def admin_required(get_user: Annotated[dict,
#                       Depends(get_current_user)]):
#     if not get_user.get("is_admin"):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You must be an admin user for this",
#         )
#     return get_user


# TODO: Либо так сделать с вложенной зависимостью, если несколько ролей
# (в том случае, если роли в отдельной таблице):
# def role_required(allowed_rolles: List[str]):
#     async def dependency(get_user: Annotated[
# dict, Depends(get_current_user)
# ]):
#         user_roles = get_user.get("roles", list())
#         if not any(role in allowed_rolles for role in user_roles):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You do not have permission to access this resource",
#             )
#         return get_user

#     return dependency

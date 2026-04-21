from fastapi import APIRouter, Depends

from app.api.security import CurrentUser, get_current_user

router = APIRouter()


@router.get("/me", summary="当前登录身份")
def get_me(user: CurrentUser = Depends(get_current_user)) -> dict[str, str]:
    return {
        "user_id": user.user_id,
        "organization_id": user.organization_id,
        "role": user.role,
        "source": user.source,
    }

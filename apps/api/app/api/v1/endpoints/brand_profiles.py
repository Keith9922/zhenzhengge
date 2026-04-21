from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_audit_service, get_brand_profile_service
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.schemas.brand_profiles import (
    BrandProfileCreateRequest,
    BrandProfileListResponse,
    BrandProfileRecord,
    BrandProfileUpdateRequest,
    SuggestConfusableResponse,
)
from app.schemas.common import ApiMessage
from app.services.brand_profiles import BrandProfileService
from app.services.audit import AuditService

router = APIRouter()


@router.get("", response_model=BrandProfileListResponse, summary="品牌权利档案列表")
def list_brand_profiles(
    service: BrandProfileService = Depends(get_brand_profile_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> BrandProfileListResponse:
    items = service.list_profiles(organization_id=resolve_scope_organization(user))
    return BrandProfileListResponse(total=len(items), items=items)


@router.post("", response_model=BrandProfileRecord, summary="创建品牌权利档案")
def create_brand_profile(
    payload: BrandProfileCreateRequest,
    service: BrandProfileService = Depends(get_brand_profile_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> BrandProfileRecord:
    scope_org = resolve_scope_organization(user) or user.organization_id
    item = service.create_profile(payload, organization_id=scope_org, owner_user_id=user.user_id)
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="brand_profile.create",
        resource_type="brand_profile",
        resource_id=item.profile_id,
        payload={"brand_name": payload.brand_name},
    )
    return item


@router.get("/{profile_id}", response_model=BrandProfileRecord, summary="品牌权利档案详情")
def get_brand_profile(
    profile_id: str,
    service: BrandProfileService = Depends(get_brand_profile_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> BrandProfileRecord:
    item = service.get_profile(profile_id, organization_id=resolve_scope_organization(user))
    if not item:
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    return item


@router.put("/{profile_id}", response_model=BrandProfileRecord, summary="更新品牌权利档案")
def update_brand_profile(
    profile_id: str,
    payload: BrandProfileUpdateRequest,
    service: BrandProfileService = Depends(get_brand_profile_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> BrandProfileRecord:
    item = service.update_profile(
        profile_id, payload, organization_id=resolve_scope_organization(user)
    )
    if not item:
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="brand_profile.update",
        resource_type="brand_profile",
        resource_id=profile_id,
        payload={},
    )
    return item


@router.delete("/{profile_id}", response_model=ApiMessage, summary="删除品牌权利档案")
def delete_brand_profile(
    profile_id: str,
    service: BrandProfileService = Depends(get_brand_profile_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> ApiMessage:
    ok = service.delete_profile(profile_id, organization_id=resolve_scope_organization(user))
    if not ok:
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="brand_profile.delete",
        resource_type="brand_profile",
        resource_id=profile_id,
        payload={},
    )
    return ApiMessage(message="已删除")


@router.post("/{profile_id}/suggest-confusable", response_model=SuggestConfusableResponse, summary="AI 生成形近混淆词")
def suggest_confusable(
    profile_id: str,
    service: BrandProfileService = Depends(get_brand_profile_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> SuggestConfusableResponse:
    item = service.get_profile(profile_id, organization_id=resolve_scope_organization(user))
    if not item:
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    suggestions = service.suggest_confusable(item.brand_name)
    return SuggestConfusableResponse(brand_name=item.brand_name, suggestions=suggestions)

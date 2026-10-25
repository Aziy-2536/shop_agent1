"""健康检查路由。

提供 ``GET /health``，用于确认服务已启动并可正常响应请求。
"""
from fastapi import APIRouter  # 路由分组，用于注册健康检查接口


# tags 用于 OpenAPI 文档分组；该接口不依赖业务服务
router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """返回固定的健康状态标识。"""
    # 只要应用能响应请求，就视为进程健康
    return {"status": "healthy"}

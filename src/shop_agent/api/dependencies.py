"""FastAPI 依赖注入。

集中定义路由所需的依赖，目前提供商品目录服务实例，
供路由函数通过 ``Depends`` 注入。
"""

from fastapi import Request  # 请求对象，可访问应用实例及其共享状态
from shop_agent.catalog.service import CatalogService  # 依赖返回值的类型标注


def get_catalog_service(request: Request) -> CatalogService:
    """从应用状态中获取商品目录服务实例。

    约定服务实例由应用创建后挂到 ``app.state.catalog_service``，
    本函数只负责按请求取出，使路由无需关心具体构造过程。

    Args:
        request: 当前请求对象，由 FastAPI 自动注入。

    Returns:
        CatalogService: 商品目录服务实例。
    """
    # 服务实例挂在应用级状态中，避免每个请求重复构造
    return request.app.state.catalog_service
"""商品目录路由。

提供 ``GET /products``，解析查询参数后委托业务服务筛选商品。
"""
from typing import Annotated  # 类型注解包装器，用于给参数附加依赖与校验元数据

from fastapi import APIRouter, Depends, Query  # 路由分组；依赖注入；查询参数校验

from shop_agent.api.dependencies import get_catalog_service  # 提供 CatalogService 的依赖函数
from shop_agent.catalog.schemas import Product  # 商品模型，用作响应结构与返回类型
from shop_agent.catalog.service import CatalogService  # 筛选业务服务，路由只负责转发参数


# 统一路由前缀为 /products；tags 用于 OpenAPI 文档分组
router = APIRouter(prefix="/products", tags=["catalog"])


# response_model 指定响应结构，FastAPI 会据此序列化并生成接口文档
@router.get("", response_model=list[Product])
def list_products(
    service: Annotated[CatalogService, Depends(get_catalog_service)],  # 由依赖注入提供服务实例
    category: Annotated[str | None, Query(min_length=1)] = None,  # 可选品类，传入时必须非空
    max_price_fen: Annotated[int | None, Query(ge=0)] = None,  # 可选最高预算（分），不能为负
) -> list[Product]:
    """返回符合条件的商品列表。

    Args:
        service: 由 FastAPI 注入的商品目录服务。
        category: 品类筛选条件；不传表示不限制。
        max_price_fen: 最高预算（单位：分）；不传表示不限制。

    Returns:
        list[Product]: 已上架且满足筛选条件的商品。
    """
    # 路由层只解析 HTTP 参数，具体筛选规则交给服务层
    return service.list_products(
        category=category,
        max_price_fen=max_price_fen,
    )

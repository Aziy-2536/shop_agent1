"""FastAPI 应用工厂。

项目采用应用工厂（factory）模式：每次调用 :func:`create_app` 都会
创建并配置一个新的 FastAPI 实例。这样可以隔离测试状态，也便于
后续按不同环境注入配置。
"""

from fastapi import FastAPI  # Web 框架核心类，用于创建应用并注册路由

from shop_agent.api.routes import health, products  # 健康检查与商品目录路由模块
from shop_agent.catalog.data import SAMPLE_PRODUCTS  # 本地种子商品，作为仓储初始数据
from shop_agent.catalog.repository import MemoryProductRepository  # 内存仓储实现
from shop_agent.catalog.service import CatalogService  # 商品筛选业务服务


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用。

    装配商品服务、创建应用实例，并注册健康检查与商品目录路由。

    Returns:
        FastAPI: 配置完成的 FastAPI 应用实例。
    """
    # 创建应用实例；title 会显示在自动生成的 OpenAPI 文档中
    app = FastAPI(title="Shop Agent API")

    # 服务实例挂在应用状态中，供依赖注入在请求期间复用
    app.state.catalog_service = CatalogService(
        MemoryProductRepository(SAMPLE_PRODUCTS)
    )

    # 按模块注册路由，各路由文件自行声明路径前缀和 OpenAPI 标签
    app.include_router(health.router)
    app.include_router(products.router)

    return app

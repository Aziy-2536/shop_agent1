"""API 接口集成测试。

通过 FastAPI 的 TestClient 在进程内发起 ASGI 请求，无需启动 uvicorn。
覆盖健康检查、商品列表筛选，以及商品模型的不可变性。
"""

import pytest  # 测试框架，用于断言异常

from fastapi.testclient import TestClient  # 进程内测试客户端，无需启动 uvicorn
from pydantic import ValidationError  # Pydantic 校验错误，用于断言不可变模型

from shop_agent.api.app import create_app  # 应用工厂，为每个测试创建独立实例


def test_health_check():
    """验证健康检查接口返回 200 和约定的状态响应体。"""
    # 每个测试用例创建独立的应用实例，避免用例之间互相影响
    client = TestClient(create_app())

    # 发起 GET 请求；TestClient 会同步执行完整的 ASGI 调用链
    response = client.get("/health")

    # 断言 HTTP 状态码为 200
    assert response.status_code == 200
    # 断言响应 JSON 与接口契约完全一致
    assert response.json() == {"status": "healthy"}


def test_products_route_filters_category_and_price() -> None:
    """验证 /products 同时按品类与最高预算筛选。"""
    # 每个用例使用独立应用，避免状态相互影响
    client = TestClient(create_app())

    # 请求咖啡品类中价格不高于 9000 分的商品
    response = client.get(
        "/products", params={"category": "咖啡", "max_price_fen": 9000}
    )

    # 接口应成功返回，且结果保持种子数据顺序
    assert response.status_code == 200
    # p002 超预算、p009 为 draft，均不应出现在结果中
    assert [product["id"] for product in response.json()] == ["p001", "p005", "p008"]


def test_shared_product_cannot_be_mutated() -> None:
    """验证商品模型不可变，避免共享的种子数据被意外修改。"""
    # 两个独立应用共享同一批冻结的 Product 实例
    first_app = create_app()
    second_app = create_app()

    product = first_app.state.catalog_service.list_products()[0]

    # frozen=True 时给字段赋值会抛 ValidationError，而不是修改对象
    with pytest.raises(ValidationError):
        product.price_fen = 1

    # 原商品价格保持不变，第二个应用读取到的数据也不受影响
    shared_product = second_app.state.catalog_service.list_products()[0]
    assert shared_product.price_fen == 8900

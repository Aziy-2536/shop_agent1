"""商品目录服务层单元测试。

覆盖“只返回已上架商品”的规则，以及品类、最高预算
两个筛选条件及其组合，全部基于本地种子数据。
"""
from shop_agent.catalog.data import SAMPLE_PRODUCTS  # 本地种子商品，作为测试数据源
from shop_agent.catalog.repository import MemoryProductRepository  # 内存仓储，避免依赖数据库
from shop_agent.catalog.service import CatalogService  # 被测的业务服务


def make_service() -> CatalogService:
    """用种子数据和内存仓储构造一个全新的服务实例。"""
    # 每个用例使用独立实例，避免测试之间共享状态
    return CatalogService(MemoryProductRepository(SAMPLE_PRODUCTS))


def test_only_active_products() -> None:
    """默认只返回已上架商品，草稿商品应被排除。"""
    # 收集商品 id，便于按种子数据直接断言返回集合
    ids = [p.id for p in make_service().list_products()]

    # 10 条种子数据中只有 p009 为 draft，因此结果为 9 条
    assert len(ids) == 9
    assert "p009" not in ids  # 草稿商品不应出现
    assert "p008" in ids      # 已上架但库存为 0，仍应返回


def test_filter_by_category() -> None:
    """按品类精确筛选，结果保持种子数据中的原始顺序。"""
    ids = [p.id for p in make_service().list_products(category="咖啡")]

    # 咖啡品类共 4 条；p008 虽然库存为 0，但已上架，仍应包含在内
    assert ids == ["p001", "p002", "p005", "p008"]


def test_filter_by_max_price() -> None:
    """按最高预算筛选，价格不超过预算的已上架商品会被返回。"""
    ids = [p.id for p in make_service().list_products(max_price_fen=5000)]

    # 5000 分 = 50 元；结果按种子数据顺序排列
    assert ids == ["p003", "p005", "p006", "p010"]


def test_combine_category_and_max_price() -> None:
    """品类与最高预算同时生效，商品需同时满足两个条件。"""
    ids = [
        p.id
        for p in make_service().list_products(
            category="咖啡", max_price_fen=9000
        )
    ]

    # 咖啡品类中排除了价格 12900 分的 p002，其余 3 条满足预算
    assert ids == ["p001", "p005", "p008"]

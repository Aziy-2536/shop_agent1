"""商品目录业务服务。

在仓储提供的全部商品之上应用业务规则：
只返回已上架商品，并可按品类和最高预算进一步筛选。
"""
from shop_agent.catalog.repository import ProductRepository  # 仓储接口，服务层依赖抽象而非具体实现
from shop_agent.catalog.schemas import Product  # 商品模型，用于标注筛选结果的元素类型


class CatalogService:
    """商品目录筛选服务。

    依赖 ``ProductRepository`` 接口读取商品，筛选规则集中在此，
    路由层与仓储层都不需要感知业务逻辑。
    """

    def __init__(self, repository: ProductRepository) -> None:
        # 保存仓储接口引用，调用 list_products 时再读取数据
        self._repository = repository

    def list_products(
        self,
        *,
        category: str | None = None,
        max_price_fen: int | None = None,
    ) -> list[Product]:
        """筛选已上架商品，可选限制品类和最高预算。

        Args:
            category: 品类；为 ``None`` 时不限制，否则要求完全相等。
            max_price_fen: 最高预算（单位：分，含边界）；为 ``None`` 时不限制。

        Returns:
            list[Product]: 满足条件的商品，保持仓储返回的顺序。
        """
        # 条件为 None 表示不限制；status 固定过滤为 active，排除草稿商品
        return [
            product
            for product in self._repository.list_products()
            if product.status == "active"
            and (category is None or product.category == category)
            and (
                max_price_fen is None
                or product.price_fen <= max_price_fen
            )
        ]

"""商品仓储层。

``ProductRepository`` 定义业务层依赖的读取接口，
``MemoryProductRepository`` 提供基于本地数据的内存实现。
"""
from collections.abc import Sequence  # 只读序列类型，用于标注商品集合
from typing import Protocol  # 结构化子类型协议，用于定义仓储接口

from shop_agent.catalog.schemas import Product  # 商品模型，仓储返回的元素类型


class ProductRepository(Protocol):
    """商品仓储接口。

    业务层只依赖该协议，不依赖具体数据来源；
    仓储负责读取全部商品，筛选由服务层完成。
    """

    def list_products(self) -> Sequence[Product]:
        """返回全部商品。

        Returns:
            Sequence[Product]: 商品序列。
        """
        ...


class MemoryProductRepository:
    """内存商品仓储实现。

    仅用于开发和测试，数据取自构造时传入的本地样例商品。
    """

    def __init__(self, products: Sequence[Product]) -> None:
        # 转为元组形成不可变快照，避免调用方后续修改原列表影响仓储数据
        self._products = tuple(products)

    def list_products(self) -> Sequence[Product]:
        """返回初始化时保存的全部商品。

        Returns:
            Sequence[Product]: 只读的商品元组。
        """
        return self._products

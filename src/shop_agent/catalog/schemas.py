"""商品目录的接口模型。

定义 API 层与业务层共用的商品数据结构 ``Product``，
由 Pydantic 负责字段类型校验与序列化。
"""
from typing import Literal  # 字面量类型，限定 status 只能取固定字符串

from pydantic import BaseModel, Field, ConfigDict  # 模型基类、字段约束与不可变模型配置


class Product(BaseModel):
    """商品。

    字段约束在实例化时由 Pydantic 自动校验，非法数据会直接报错。
    """
    model_config = ConfigDict(frozen=True)  # 模型实例不可变，避免被意外修改
    id: str = Field(min_length=1)          # 商品唯一标识，如 "p001"
    name: str = Field(min_length=1)        # 商品展示名称
    category: str = Field(min_length=1)    # 商品品类，用于按品类筛选
    price_fen: int = Field(ge=0)           # 价格，单位为“分”，用整数避免浮点误差
    stock: int = Field(ge=0)               # 库存数量，0 表示暂时无货
    status: Literal["active", "draft"]     # 上架状态：active=已上架，draft=未上架
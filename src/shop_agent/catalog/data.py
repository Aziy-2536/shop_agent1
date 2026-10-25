"""本地商品种子数据。

提供第一阶段所需的 10 条商品数据，字段覆盖品类、价格与上架状态，
作为内存仓储的初始数据来源。
"""
from shop_agent.catalog.schemas import Product  # 商品模型，导入种子数据时完成校验


# 10 条种子商品，覆盖“咖啡 / 茶具 / 杯具”三个品类；
# 价格分布不同，且 p009 是唯一的 draft 商品，
# 便于测试品类、最高预算、上架状态三个筛选条件及其组合。
SAMPLE_PRODUCTS: tuple[Product, ...] = (
    Product(id="p001", name="手冲咖啡壶", category="咖啡", price_fen=8900, stock=12, status="active"),
    Product(id="p002", name="便携磨豆机", category="咖啡", price_fen=12900, stock=8, status="active"),
    Product(id="p003", name="玻璃茶杯", category="茶具", price_fen=3900, stock=20, status="active"),
    Product(id="p004", name="旅行保温杯", category="杯具", price_fen=6900, stock=15, status="active"),
    Product(id="p005", name="咖啡滤纸", category="咖啡", price_fen=1500, stock=100, status="active"),
    Product(id="p006", name="陶瓷马克杯", category="杯具", price_fen=4900, stock=10, status="active"),
    Product(id="p007", name="入门茶壶", category="茶具", price_fen=9900, stock=4, status="active"),
    Product(id="p008", name="咖啡分享壶", category="咖啡", price_fen=7900, stock=0, status="active"),
    Product(id="p009", name="新品冰杯", category="杯具", price_fen=5900, stock=6, status="draft"),
    Product(id="p010", name="茶叶收纳罐", category="茶具", price_fen=2900, stock=30, status="active"),
)
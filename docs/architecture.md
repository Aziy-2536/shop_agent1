# Shop Agent 项目架构与代码导读

> 最后更新：2026-10-25
>
> 本文档以**当前仓库中的实际代码**为准，用于快速理解项目结构、各模块职责和现有实现边界。

## 1. 项目概览

Shop Agent 是一个模块化电商导购 Agent 项目。第一阶段的目标是：

- 提供 `GET /health` 健康检查接口；
- 提供 `GET /products` 商品列表接口；
- 准备 10 条本地商品数据；
- 支持按品类和最高预算筛选，固定只返回已上架商品，并编写测试。

当前实现情况：

- `GET /health` 与 `GET /products` 均已注册并可访问；
- 商品模型、10 条种子数据、内存仓储和筛选服务均已接通；
- 支持按品类和最高预算筛选，且只返回已上架商品；
- 共有 6 个测试通过：2 个接口集成测试 + 4 个服务层单元测试。

尚未实现的部分：

- 商家端查看草稿商品的独立授权接口；当前顾客接口固定只返回 `active` 商品；
- `api/errors.py` 统一异常处理；
- `core/config.py`、`core/exceptions.py` 的具体内容。

## 2. 技术栈

| 技术 | 用途 |
| --- | --- |
| Python 3.13+ | 开发语言 |
| FastAPI | Web 框架与自动 OpenAPI 文档 |
| Uvicorn | ASGI 服务器，运行 FastAPI 应用 |
| Pydantic | 数据模型校验与序列化 |
| pytest | 测试框架 |
| httpx / TestClient | 进程内发起 ASGI 请求的测试客户端 |
| uv | 依赖管理与项目运行 |

项目采用 `src` 布局，包名为 `shop_agent`，由 `pyproject.toml` 中的 hatchling 配置打包。

## 3. 目录结构

```text
agent_2/
├─ main.py                          # 本地启动入口：用 uvicorn 启动应用
├─ pyproject.toml                   # 项目元数据、依赖、pytest 配置
├─ README.md                        # 运行说明与架构入口
├─ docs/
│  └─ architecture.md               # 本文档
├─ src/
│  └─ shop_agent/
│     ├─ __init__.py                # 包说明
│     ├─ api/                       # API 接口层
│     │  ├─ app.py                  # 应用工厂：装配服务、注册各模块路由
│     │  ├─ dependencies.py         # get_catalog_service：从 app.state 取服务
│     │  ├─ errors.py               # API 错误处理（预留）
│     │  └─ routes/
│     │     ├─ __init__.py          # 路由包说明
│     │     ├─ health.py            # GET /health
│     │     └─ products.py          # GET /products
│     ├─ catalog/                   # 商品目录领域
│     │  ├─ schemas.py              # Product 数据模型
│     │  ├─ data.py                 # 10 条本地种子商品
│     │  ├─ repository.py           # 仓储协议 + 内存实现
│     │  └─ service.py              # 商品筛选业务逻辑
│     └─ core/                      # 核心基础设施
│        ├─ config.py               # 应用配置（预留）
│        └─ exceptions.py           # 领域异常（预留）
└─ tests/
   ├─ test_app.py                   # /health 与 /products 接口集成测试
   └─ catalog/
      └─ test_service.py            # 4 个商品服务单元测试
```

## 4. 分层与依赖关系

项目是一个按“功能模块 + 分层”组织的单体应用，当前依赖流向如下：

```text
main.py
  │ 启动（uvicorn 应用工厂模式）
  ▼
api/app.py : create_app()
  │
  ├── app.state.catalog_service = CatalogService(MemoryProductRepository(SAMPLE_PRODUCTS))
  │
  ├── include_router(health.router)
  │     └── api/routes/health.py : GET /health → {"status": "healthy"}
  │
  └── include_router(products.router)
        └── api/routes/products.py : GET /products
              │ Depends(get_catalog_service)
              ▼
        api/dependencies.py : get_catalog_service()
              │ request.app.state.catalog_service
              ▼
        catalog/service.py : CatalogService
              │ 依赖 ProductRepository 协议
              ▼
        catalog/repository.py : MemoryProductRepository
              │ 读取并返回 Product 序列
              ▼
        catalog/schemas.py : Product
              ▲
              │ 构造
        catalog/data.py : SAMPLE_PRODUCTS
```

分层职责：

| 层 | 位置 | 职责 | 当前状态 |
| --- | --- | --- | --- |
| 接口层 | `src/shop_agent/api/` | 创建应用、注册路由、依赖注入、错误转换 | `/health`、`/products` 已接通；错误处理预留 |
| 领域层 | `src/shop_agent/catalog/` | 商品模型、数据来源、仓储与业务规则 | 已全部实现 |
| 基础设施 | `src/shop_agent/core/` | 配置、异常等跨模块能力 | 均为预留 |
| 测试 | `tests/` | 集成测试与单元测试 | 6 个测试通过 |

核心原则：**路由只负责参数和 HTTP 语义，筛选规则放在服务层，数据读取放在仓储层**。这样更换数据来源时不需要改动业务逻辑。

## 5. 各模块说明

### 5.1 启动入口：`main.py`

```python
uvicorn.run(
    "shop_agent.api.app:create_app",
    factory=True,
    host="127.0.0.1",
    port=8000,
)
```

- `main()` 只在直接执行 `python main.py` 时运行；
- `factory=True` 表示 `模块:属性` 指向的是**工厂函数**，uvicorn 会调用它并以其返回值作为 ASGI 应用；
- 默认只监听本机 `127.0.0.1:8000`。

### 5.2 API 层：`src/shop_agent/api/`

#### `app.py`

- 采用应用工厂模式：`create_app()` 每次调用都会创建新的 `FastAPI` 实例；
- 应用标题为 `Shop Agent API`，自动生成 `/docs`、`/redoc` 和 `/openapi.json`；
- 创建服务实例并挂到 `app.state.catalog_service`，供依赖注入读取；
- 通过 `app.include_router()` 注册 `health` 和 `products` 两个路由模块；
- 健康检查的响应为 `{"status": "healthy"}`；
- 测试中通过工厂创建独立实例，避免用例之间共享状态。

#### `dependencies.py`

已实现 `get_catalog_service(request)`：

- 从 `request.app.state.catalog_service` 取出商品目录服务实例；
- 路由通过 `Annotated[CatalogService, Depends(get_catalog_service)]` 获取该依赖；
- 服务实例在应用创建时构造一次，后续请求复用，不需要在每个请求中重复创建。

#### `routes/`

- `health.py`：使用 `APIRouter(tags=["system"])` 定义 `GET /health`，只返回固定健康状态，不依赖业务服务；
- `products.py`：定义 `GET /products`、校验查询参数并调用商品服务；
- 两个路由由 `app.py` 集中注册，商品业务规则仍位于 `catalog/service.py`；
- 在新增路由时，按模块拆分文件并在 `app.py` 中注册即可，不需要把 HTTP 细节放进领域层。

`products.py` 使用 `APIRouter(prefix="/products", tags=["catalog"])`，以
`list[Product]` 为响应结构。可选参数 `category` 要求非空，`max_price_fen`
要求非负；它们经 `Depends(get_catalog_service)` 交给服务层处理。参数不合法时
FastAPI 返回 `422`。

#### `errors.py`（预留）

后续用于注册 FastAPI 异常处理器，把 `core/exceptions.py` 中的领域异常转换成统一的 HTTP 错误响应（状态码 + 错误体）。

### 5.3 商品目录：`src/shop_agent/catalog/`

#### `schemas.py` — 商品模型

`Product` 是一个 Pydantic 模型，实例化时会自动校验字段：

| 字段 | 类型 | 约束 | 含义 |
| --- | --- | --- | --- |
| `id` | `str` | 非空 | 商品唯一标识，如 `"p001"` |
| `name` | `str` | 非空 | 商品名称 |
| `category` | `str` | 非空 | 商品品类 |
| `price_fen` | `int` | `>= 0` | 价格，单位为**分** |
| `stock` | `int` | `>= 0` | 库存数量，`0` 表示无货 |
| `status` | `Literal["active", "draft"]` | 二选一 | `active`=已上架，`draft`=未上架 |

价格使用整数“分”而不是浮点“元”，可以避免金额计算中的浮点误差。

#### `data.py` — 本地种子数据

`SAMPLE_PRODUCTS` 是一个 `tuple[Product, ...]`，包含 10 条商品：

- 覆盖 3 个品类：咖啡（4 条）、茶具（3 条）、杯具（3 条）；
- 价格从 15 元到 129 元不等；
- `p008`（咖啡分享壶）库存为 `0`，但仍然已上架；
- `p009`（新品冰杯）是唯一的 `draft` 商品。

这些数据既用于本地开发，也用于覆盖筛选条件的测试场景。完整数据见 `src/shop_agent/catalog/data.py`。

#### `repository.py` — 仓储层

包含两部分：

1. **`ProductRepository`（Protocol）**
   - 定义仓储需要满足的接口：`list_products() -> Sequence[Product]`；
   - 业务层只依赖该协议，不依赖具体实现；
   - 仓储只负责读取全部商品，**筛选逻辑由服务层负责**。

2. **`MemoryProductRepository`**
   - 内存实现，仅用于开发和测试；
   - 构造时把传入的商品序列转成元组，形成不可变快照；
   - `list_products()` 原样返回内部元组。

服务层通过协议类型接收仓储，后续接入数据库或远程服务时，只需提供新的实现，不需要修改筛选逻辑。

#### `service.py` — 业务服务

`CatalogService` 依赖 `ProductRepository`，提供商品筛选能力：

```python
class CatalogService:
    def __init__(self, repository: ProductRepository) -> None: ...

    def list_products(
        self,
        *,
        category: str | None = None,
        max_price_fen: int | None = None,
    ) -> list[Product]: ...
```

当前实现的筛选规则：

1. **只保留 `status == "active"` 的商品**，`draft` 商品始终不会返回；
2. `category` 为空时不过滤，否则要求品类**完全相等**；
3. `max_price_fen` 为空时不过滤，否则要求 `price_fen <= max_price_fen`（包含边界值）；
4. 所有条件需同时满足；
5. 参数使用 `*` 声明为关键字参数，调用时必须写成 `list_products(category=..., max_price_fen=...)`。

当前顾客商品接口没有 `status` 查询参数，始终只返回 `active` 商品。
若后续增加商家端草稿查询，应在商家身份与权限边界下单独设计。

### 5.4 核心基础设施：`src/shop_agent/core/`

- `config.py`（预留）：集中读取环境变量，例如主机、端口、数据来源等配置；
- `exceptions.py`（预留）：定义 API 层可统一识别和处理的领域异常。

### 5.5 测试：`tests/`

- `test_app.py`：使用 `TestClient(create_app())` 在进程内发起请求，包含 2 个用例：
  - `test_health_check`：验证 `/health` 返回 200 和 `{"status": "healthy"}`；
  - `test_products_route_filters_category_and_price`：请求 `/products?category=咖啡&max_price_fen=9000`，断言返回商品 id 为 `["p001", "p005", "p008"]`。
- `catalog/test_service.py`：直接测试 `CatalogService`，共 4 个用例：
  - `test_only_active_products`：默认只返回已上架商品，`p009` 被排除，库存为 0 的 `p008` 仍然返回；
  - `test_filter_by_category`：按品类精确筛选；
  - `test_filter_by_max_price`：按最高预算筛选；
  - `test_combine_category_and_max_price`：品类与最高预算组合筛选。

服务测试通过 `make_service()` 为每个用例创建独立的服务实例（内存仓储 + 种子数据），避免用例之间共享状态。

## 6. 请求流程

### 6.1 `/health`

```text
客户端 / TestClient
      │ GET /health
      ▼
api/routes/health.py : health_check()
      │
      ▼
返回 200 {"status": "healthy"}
```

### 6.2 `/products`

```text
客户端
  │ GET /products?category=咖啡&max_price_fen=9000
  ▼
api/routes/products.py : list_products()
  │ Depends(get_catalog_service)
  ▼
api/dependencies.py : get_catalog_service()
  │ request.app.state.catalog_service
  ▼
CatalogService.list_products(category="咖啡", max_price_fen=9000)
  │ 从仓储读取全部商品
  ▼
MemoryProductRepository.list_products()
  │ 返回 10 条种子商品
  ▼
服务层过滤：status == "active" + 品类 + 最高预算
  │
  ▼
FastAPI 按 list[Product] 序列化为 JSON 并返回
```

示例：`GET /products?category=咖啡&max_price_fen=9000` 会返回商品 id 为 `p001`、`p005`、`p008` 的完整商品对象；其中 `p002` 因价格 12900 分超过预算被排除，`p009` 因处于 `draft` 状态被排除。

## 7. 本地运行与测试

```powershell
# 安装/同步依赖
uv sync

# 启动服务（应用工厂模式）
uv run python main.py
```

启动后可访问：

- 健康检查：`http://127.0.0.1:8000/health`
- 商品列表：`http://127.0.0.1:8000/products`
- 交互式文档：`http://127.0.0.1:8000/docs`

运行测试：

```powershell
uv run pytest -q
```

当前测试结果：`6 passed`（2 个接口集成测试 + 4 个商品服务单元测试）。

## 8. 当前实现状态一览

| 文件 | 状态 | 说明 |
| --- | --- | --- |
| `main.py` | 已实现 | uvicorn 启动入口，工厂模式 |
| `api/app.py` | 已实现 | 应用工厂；挂载服务、注册 `/health` 与 `/products` |
| `api/dependencies.py` | 已实现 | `get_catalog_service()` 从 `app.state` 读取服务 |
| `api/errors.py` | 预留 | 规划用于统一异常响应 |
| `api/routes/health.py` | 已实现 | `GET /health` 路由 |
| `api/routes/products.py` | 已实现 | `GET /products` 路由与查询参数校验 |
| `catalog/schemas.py` | 已实现 | `Product` 模型 |
| `catalog/data.py` | 已实现 | 10 条种子商品 |
| `catalog/repository.py` | 已实现 | `ProductRepository` 协议 + `MemoryProductRepository` |
| `catalog/service.py` | 已实现 | 只返回 active 商品，支持品类、最高预算筛选 |
| `core/config.py` | 预留 | 规划集中管理配置 |
| `core/exceptions.py` | 预留 | 规划定义领域异常 |
| `tests/test_app.py` | 已实现 | `/health` 与 `/products` 集成测试 |
| `tests/catalog/test_service.py` | 已实现 | 4 个商品服务单元测试 |

## 9. 推荐阅读顺序

如果从零开始阅读代码，建议按以下顺序：

1. `main.py`：了解应用如何启动；
2. `api/app.py`：了解应用如何装配服务和注册路由；
3. `catalog/schemas.py`：了解商品的数据结构；
4. `catalog/data.py`：了解本地有哪些商品；
5. `catalog/repository.py`：了解商品如何被读取、为何使用 Protocol；
6. `catalog/service.py`：了解筛选规则；
7. `api/routes/products.py`：了解查询参数与依赖注入；
8. `api/dependencies.py`：了解服务实例如何交给路由；
9. `tests/catalog/test_service.py`：了解服务层行为如何被测试；
10. `tests/test_app.py`：了解如何用 TestClient 测试完整接口；
11. 最后查看各预留模块的 docstring，了解后续扩展点。

## 10. 后续建议

1. **商家商品管理**：按商家身份和权限设计草稿查询与维护接口；
2. **补充接口边界测试**：覆盖不带筛选参数、非法参数（如空品类、负预算）、空结果等场景；
3. **接通异常处理**：在 `core/exceptions.py` 定义异常，在 `api/errors.py` 注册处理器；
4. **按需实现配置模块**：集中管理主机、端口和数据来源；
5. **补充接口说明**：在 README 中加入常用查询示例；
6. **补充新增文件注释**：`api/routes/health.py`、`api/routes/products.py` 和 `test_app.py` 可继续按现有中文注释风格完善说明。

> 当前代码已可运行，测试全部通过；商家商品管理、异常处理和配置模块仍待实现。

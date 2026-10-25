# Shop Agent

当前已实现健康检查和基于本地样例数据的商品列表接口。

`pyproject.toml`、`uv.lock`、`.python-version` 和 `.gitignore` 保留，方便安装依赖和后续开发。

`api/app.py` 统一创建应用、装配服务并注册路由；接口定义位于 `api/routes/`，商品筛选规则位于 `catalog/service.py`。详细结构见 [架构说明](docs/architecture.md)。

```powershell
uv sync
uv run python main.py
```

启动后访问 `/health`、`/products` 或 `/docs`。运行测试：`uv run pytest -q`。

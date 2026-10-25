"""Shop Agent 本地启动入口。

直接运行本文件（``python main.py``）时，通过 uvicorn 启动
FastAPI 应用，默认监听 127.0.0.1:8000，用于本地开发与调试。
"""

import uvicorn  # ASGI 服务器，用于加载并运行 FastAPI 应用


def main():
    """启动 Shop Agent API 服务。

    这里使用 uvicorn 的“应用工厂”模式：
    ``factory=True`` 时，uvicorn 会调用 ``模块:属性`` 指向的可调用对象，
    并用其返回值作为 ASGI 应用，而不是直接使用模块级应用实例；
    因此目标字符串指向 ``app.py`` 中的 ``create_app``。
    """
    uvicorn.run(
        "shop_agent.api.app:create_app",  # 待加载的模块与属性（工厂模式下的工厂函数名）
        factory=True,              # 以工厂方式调用该属性，获取 FastAPI 实例
        host="127.0.0.1",          # 仅监听本机地址，不对外网开放
        port=8000,                 # 本地开发使用的端口
    )


if __name__ == "__main__":
    # 仅当本文件被直接执行时启动服务；被 import 时不会运行
    main()

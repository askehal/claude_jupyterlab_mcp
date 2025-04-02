from setuptools import setup

setup(
    name="claude-jupyter-mcp",
    version="0.1",
    py_modules=["claude_mcp", "claude_extension", "simple_magic"],
    install_requires=[
        "jupyterlab",
        "anthropic",
        "ipywidgets",
    ],
)
from setuptools import setup, find_packages

setup(
    name="claudek",
    version="0.2.0",
    packages=find_packages(),
    py_modules=["agent_coding"],
    install_requires=[
        "pydantic",
        "rich",
        "requests",
        "pytest",
        "pytest-asyncio"
    ],
    scripts=["bin/claudek"],
    entry_points={
        "console_scripts": [
            "claudek=agent_coding.cli:main",
            "agent-coding=agent_coding.cli:main",
        ],
    },
    author="Jules Agent",
    description="Claude Code terminal TUI & Web UI coding agent",
    python_requires=">=3.10",
)

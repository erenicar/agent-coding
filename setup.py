from setuptools import setup, find_packages

setup(
    name="agent-coding",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["agent_coding"],
    install_requires=[
        "pydantic",
        "rich",
        "requests",
        "pytest",
        "pytest-asyncio"
    ],
    scripts=["bin/agent-coding"],
    author="Jules Agent",
    description="Claude Code style desktop coding agent environment",
    python_requires=">=3.10",
)

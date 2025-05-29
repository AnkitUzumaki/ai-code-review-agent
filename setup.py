# setup.py
from setuptools import setup, find_packages

setup(
    name="ai-code-review-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "autopep8>=2.0.0",
        "ruff>=0.6.0",
        "pylint>=2.17.0",
        "bandit>=1.7.0",
        "radon>=5.1.0",
        "pytest>=7.0.0",
        "flask>=2.0.0",
        "weasyprint>=52.0",
        "memory-profiler>=0.61.0",
        "gitpython>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-code-review=src.main:main",
        ],
    },
)



from setuptools import setup, find_packages

setup(
    name="hackmit-agent",
    version="0.1.0",
    description="Fetch.ai Agent System for Healthcare Voice Processing",
    packages=find_packages(),
    install_requires=[
        "aea[all]==1.0.0",
        "flask==2.3.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "pydantic==2.4.2",
        "uvicorn==0.23.2",
        "fastapi==0.103.2",
    ],
    python_requires=">=3.8",
)

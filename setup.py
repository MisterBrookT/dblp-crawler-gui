from setuptools import setup, find_packages

setup(
    name="dblp-crawler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        # Add any other dependencies your project needs
    ],
)
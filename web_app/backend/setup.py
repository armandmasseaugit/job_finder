from setuptools import setup, find_packages

setup(
    name="web_app_backend",
    version="0.1",
    packages=find_packages(include=["routes*", "services*"]),
)

from setuptools import setup, find_packages

setup(
    name="open_banking_api_mock",
    version="0.1",
    description="Mock API for Open Banking services",
    author="Kirill Krasnoslobodtsev",
    author_email="lyrics.red@yandex.ru",
    url="https://github.com/lyricsred/OpenBankingApiMock",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "PyJWT>=2.6.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)
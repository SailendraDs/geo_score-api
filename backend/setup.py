from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geoscore",
    version="0.1.0",
    author="Sailendra Damaraju",
    author_email="admin@geoscore.in",
    description="A FastAPI-based service for scoring geographical entities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SailendraDs/geo_score-api",
    packages=find_packages(include=['*'], exclude=['tests*']),
    package_dir={"": "."},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.19.0,<1.0.0",
        "requests>=2.26.0,<3.0.0",
        "beautifulsoup4>=4.9.3,<5.0.0",
        "wikipedia-api>=0.5.4,<1.0.0",
        "openai>=0.27.0,<1.0.0",
        "google-api-python-client>=2.0.0,<3.0.0",
        "python-multipart>=0.0.5,<1.0.0",
        "fake-useragent>=1.1.3,<2.0.0",
        'aiosqlite>=0.18.0',
        'httpx>=0.23.0',
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5,<7.0.0",
            "pytest-cov>=2.12.0,<3.0.0",
            "black>=21.9b0,<22.0.0",
            "flake8>=4.0.0,<5.0.0",
            "isort>=5.9.3,<6.0.0",
            "mypy>=0.910,<1.0.0",
            "httpx>=0.19.0,<1.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'geoscore=main:main',
        ],
    },
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geoscore",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A FastAPI-based service for scoring geographical entities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/geoscore",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.68.0,<1.0.0",
        "uvicorn>=0.15.0,<1.0.0",
        "python-dotenv>=0.19.0,<1.0.0",
        "requests>=2.26.0,<3.0.0",
        "beautifulsoup4>=4.9.3,<5.0.0",
        "wikipedia-api>=0.5.4,<1.0.0",
        "openai>=0.27.0,<1.0.0",
        "google-api-python-client>=2.0.0,<3.0.0",
        "pydantic>=1.8.0,<2.0.0",
        "python-multipart>=0.0.5,<1.0.0",
        "fake-useragent>=1.1.3,<2.0.0",
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
        "console_scripts": [
            "geoscore=main:main",
        ],
    },
    include_package_data=True,
)

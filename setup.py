from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lemmo-be-core",
    version="0.1.0",
    description="Lemmo Backend Core Package - Essential utilities, models, and GraphQL infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="2MCorp",
    author_email="contact@2mcorp.com",
    url="https://github.com/2mcorp/lemmo-be-core",
    packages=find_packages(),
    install_requires=[
        "django>=4.2,<5.0",
        "graphene-django>=3.0,<4.0",
        "pyyaml>=6.0,<7.0",
        "typing-extensions>=4.0,<5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0,<8.0",
            "pytest-django>=4.0,<5.0",
            "black>=23.0,<24.0",
            "flake8>=6.0,<7.0",
            "mypy>=1.0,<2.0",
            "types-PyYAML>=6.0,<7.0",
        ],
        "test": [
            "pytest>=7.0,<8.0",
            "pytest-django>=4.0,<5.0",
            "factory-boy>=3.0,<4.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    zip_safe=False,
    keywords="django, graphql, core, utilities, models, authentication",
    project_urls={
        "Bug Reports": "https://github.com/2mcorp/lemmo-be-core/issues",
        "Source": "https://github.com/2mcorp/lemmo-be-core",
        "Documentation": "https://github.com/2mcorp/lemmo-be-core#readme",
    },
)

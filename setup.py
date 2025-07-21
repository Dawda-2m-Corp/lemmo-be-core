from setuptools import setup, find_packages

setup(
    name="lemmo-be-core",
    version="0.1.0",
    description="Lemmo Backend Core Package",
    author="2MCorp",
    author_email="contact@2mcorp.com",
    packages=find_packages(),
    install_requires=[
        "django",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.13",
)

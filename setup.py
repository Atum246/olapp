"""Setup script for olapp."""
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

# Read version
version = {}
with open(os.path.join(here, "olapp", "version.py")) as f:
    exec(f.read(), version)

# Read README
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="olapp",
    version=version["__version__"],
    author="Olapp Team",
    author_email="hello@olapp.dev",
    description="A modern alternative to Gradio with stunning UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olapp/olapp",
    packages=find_packages(),
    package_data={
        "olapp": [
            "static/*.css",
            "static/*.js",
            "templates/*.html",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.18",
            "aiohttp[speedups]",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="gradio ui web ml machine-learning demo",
    entry_points={},
)

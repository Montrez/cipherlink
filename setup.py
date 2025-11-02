"""
Setup configuration for Cipherlink.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cipherlink",
    version="0.1.0",
    author="Cipherlink Team",
    description="Lightweight peer-to-peer VPN built in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        req for req in requirements if not any(req.startswith(x) for x in ["pytest", "black", "flake8", "mypy"])
    ],
    entry_points={
        "console_scripts": [
            "cipherlink-genkeys=scripts.genkeys:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)


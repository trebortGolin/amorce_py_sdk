from setuptools import setup, find_packages
from pathlib import Path

# Read README for the long description on PyPI
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else "Official Nexus Protocol SDK"

setup(
    name="nexus-py-sdk",
    version="0.1.6",  # BUMP: 0.1.5 -> 0.1.6 (Critical API Fix: Agent ID Derivation)
    description="Official Python SDK for the Nexus Agent Transaction Protocol (NATP)",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Athena Architecture",
    author_email="dev@amorce.io",
    url="https://github.com/trebortGolin/nexus_py_sdk",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "cryptography>=41.0.0",
        "pydantic>=2.0.0",
        "google-cloud-secret-manager>=2.16.0",
        "firebase-admin>=6.2.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
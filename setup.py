from setuptools import setup, find_packages
from pathlib import Path

# Read README for the long description on PyPI (Best practice)
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else "Official Nexus Protocol SDK"

setup(
    name="nexus-py-sdk",
    version="0.1.2",  # BUMP: 0.1.0 -> 0.1.2 (Priority Lane + Resilience)
    description="Official Python SDK for the Nexus Agent Transaction Protocol (NATP)",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Athena Architecture",
    author_email="dev@amorce.io", # Dummy email for the package
    url="https://github.com/trebortGolin/nexus_py_sdk", # Your GitHub URL
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "cryptography>=43.0.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        # google-cloud-secret-manager is optional in dev, but required in prod.
        # Keeping it here for now.
        "google-cloud-secret-manager>=2.16.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
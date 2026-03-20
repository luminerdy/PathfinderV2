"""
Pathfinder Robot Framework Setup
"""

from setuptools import setup, find_packages

setup(
    name="pathfinder",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "opencv-python>=4.8.0",
        "pyserial>=3.5",
    ],
    python_requires=">=3.9",
)

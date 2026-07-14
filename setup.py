from setuptools import find_packages, setup
import sys
from pathlib import Path

setup(
    name="pycarlanet",
    packages=find_packages(include=['pycarlanet', 'pycarlanet.utils', 'pycarlanet.enum', 'pycarlanet.listeners']),
    version="2.0",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type='text/markdown',
    author="Valerio Cislaghi, Christian Quadri, Stefano di Terlizzi",
    license='MIT',
    python_requires='>=3.6,<3.13',
    install_requires=[
        'pyzmq==27.1.0',
        'carla==0.9.16'
    ],
    project_urls={
        'Source': 'https://github.com/jaivra/pycarlanet',
    },
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest==7.2.1'
    ],
    test_suite='tests'
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)

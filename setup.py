from setuptools import find_packages, setup
import sys

setup(
    name="pycarlanet",
    packages=find_packages(include=['pycarlanet', 'pycarlanet.utils']),
    version="0.8.5-alpha",
    long_description="""Carla and Omnet++ co-simulation library""",
    long_description_content_type='text/markdown',
    author="Valerio Cislaghi, Christian Quadri",
    license='MIT',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,<3.9',
    install_requires=[
        'pyzmq==23.2.1',
        'carla==0.9.13'
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
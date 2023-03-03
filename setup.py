from setuptools import find_packages, setup

setup(
    name="pycarlanet",
    packages=find_packages(include=['pycarlanet', 'pycarlanet.utils']),
    version="0.8.0-alpha",
    description='Carla and Omnet++ co-simulation library',
    author="Valerio Cislaghi, Christian Quadri",
    license='MIT',
    install_requires=[
        'pyzmq==23.2.1',
        'carla==0.9.13'
    ],
    project_urls={
        'Source': 'https://github.com/jaivra/pycarlanet',
    },
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest==4.4.1'
    ],
    test_suite='tests'
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)
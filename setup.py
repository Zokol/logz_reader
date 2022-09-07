from setuptools import setup

setup(
    name='logz_reader',
    version='0.1',
    packages=['logzreader'],
    install_requires=[
        'click>=8.1.3',
        'requests>=2.28.1',
        'pytz>=2022.2.1',
        'python-dotenv>=0.21.0'
    ],
    tests_require=['unittest'],
    url='https://github.com/Zokol/logz_reader',
    license='Creative Commons Attribution-ShareAlike 4.0 International',
    author='Heikki "zokol" Juva',
    description='Logz.io API Reader'
)


from setuptools import setup, find_packages

setup(
    name='scrapkit',
    version='0.1.7',
    packages=find_packages(),
    author='Ashwin',
    author_email='surana.an@gmail.com',
    description='A utility library for scraping.',
    url='https://github.com/Ashwin-Surana/scrapkit',
    install_requires=[
        'requests',
    ],
    zip_safe=False
)

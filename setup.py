from setuptools import setup

setup(
    name='scrapkit',
    version='0.1',
    packages= ['scrapkit'],
    author='Ashwin',
    author_email='surana.an@gmail.com',
    description='A utility library for scraping.',
    url='https://github.com/Ashwin-Surana/scrapkit',
    install_requires=[
        'requests',
    ],
    zip_safe=False
)

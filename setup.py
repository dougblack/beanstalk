from setuptools import setup, find_packages

setup(
    name='beanstalk',
    version='0.0.1',
    description='Netrunner Discord bot',
    author='Doug Black',
    author_email='doug@dougblack.io',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'discord.py',
        'fuzzywuzzy',
        'python-Levenshtein',
    ],
)

from setuptools import setup, find_packages

# Read the requirements.txt file to avoid duplicating dependencies here
def parse_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line and not line.startswith('#')]

setup(
    name='golf-better-common',
    version='0.1.0',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    url='https://github.com/cfredericks/golf-better',
)
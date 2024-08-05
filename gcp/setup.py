from setuptools import setup, find_packages

# Read the requirements.txt file to avoid duplicating dependencies here
def parse_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line and not line.startswith('#')]

setup(
    name='golf-better',
    version='0.1',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
)
from setuptools import setup, find_packages
from pathlib import Path

from vaultsafe.config import GITHUB_REPO

# Define the base directory
base_dir = Path(__file__).resolve().parent

# Read the version from password_manager/version.py
version = {}
version_path = base_dir / 'vaultsafe' / 'version.py'
with open(version_path) as f:
    exec(f.read(), version)

# Read the long description from README.md
long_description = (base_dir / 'README.md').read_text()

# Generate the install_requires list from requirements.txt
install_requires = (base_dir / 'requirements.txt').read_text().splitlines()

setup(
    name='vaultsafe',
    version=version['__version__'],  # Update version if necessary
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'vaultsafe=vaultsafe.cli:cli',
        ],
    },
    author='Indrajit Ghosh',
    author_email='indrajitghosh912@gmail.com',
    description='A CLI-based password manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=GITHUB_REPO,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
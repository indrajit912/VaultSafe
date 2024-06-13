# This script contains the setup script for installing the package.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024

from setuptools import setup, find_packages

setup(
    name='password_manager',
    version='0.1.0',
    packages=find_packages(),  # This should find all packages under password_manager
    include_package_data=True,  # This includes files specified in MANIFEST.in
    install_requires=[
        'SQLAlchemy',
        'cryptography',
        'click',
        'pyperclip',
        'pwinput',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'password-manager=password_manager.cli:cli',
        ],
    },
    author='Indrajit Ghosh',
    author_email='indrajitghosh912@gmail.com',
    description='A CLI-based password manager',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/indrajit912/PasswordManager.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

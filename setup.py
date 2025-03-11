from setuptools import setup, find_packages

setup(
    name="ptodo",
    version="1.0.0",
    description="Plaintext Todo.txt CLI",
    author="Aaron Wilson",
    author_email="aaron@acwilson.dev",
    url="https://github.com/awilsoncs/ptodo",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ptodo=ptodo:main",
        ],
    },
    install_requires=[
        # List your dependencies here
    ],
    extras_require={
        'dev': [
            'black>=23.12.0',  # supports Python 3.12
            'isort>=5.13.0',   # supports Python 3.12
            'flake8>=7.0.0',   # supports Python 3.12
            'mypy>=1.8.0',     # supports Python 3.12
        ],
        'test': [
            'pytest>=8.0.0',   # supports Python 3.12
            'pytest-cov>=4.1.0', # supports Python 3.12
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)


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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


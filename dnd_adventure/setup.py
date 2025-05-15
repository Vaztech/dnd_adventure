from setuptools import setup, find_packages

setup(
    name="dnd_adventure",
    version="0.1",
    packages=find_packages(),
    
    # Metadata
    author="Vaz",
    author_email="your.email@example.com",
    description="A Python package for D&D adventure generation and management",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Vaztech/dnd_adventure",
    project_urls={
        "Bug Tracker": "https://github.com/Vaztech/dnd_adventure/issues",
        "Documentation": "https://github.com/Vaztech/dnd_adventure/wiki",
        "Source Code": "https://github.com/Vaztech/dnd_adventure",
    },
    
    # Classifiers help users find your project by categorizing it
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust as needed
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Role-Playing",
    ],
    
    # Dependencies
    install_requires=[
        # List your package dependencies here, for example:
        # "numpy>=1.18.0",
        # "pandas>=1.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=20.8b1",
            "flake8>=3.8.0",
        ],
    },
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Include non-python files (adjust as needed)
    package_data={
        "dnd_adventure": ["data/*.json", "templates/*.txt"],
    },
    
    # Entry points (CLI commands)
    entry_points={
        "console_scripts": [
            "dnd-adventure=dnd_adventure.cli:main",
        ],
    },
)
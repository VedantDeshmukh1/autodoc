from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autodoc",
    version="0.2.0",
    author="Vedant Deshmukh",
    author_email="vedantdeshmukh1983@gmail.com",
    description="A robust package for automatically generating interactive documentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VedantDeshmukh1/autodoc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Jinja2>=2.11.3",
        "markdown2>=2.4.0",
        "Pygments>=2.8.1",
        "radon>=5.1.0",
        
    ],
    extras_require={
        "nlp": ["nltk>=3.6.2"],
    },
    include_package_data=True,
    package_data={
        "autodoc": ["templates/*", "static/*"],
    },
)
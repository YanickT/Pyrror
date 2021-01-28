import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logik",
    version="0.0.1",
    author="Yanick T.",
    description="Package for uncertainty propagation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YanickT/Pyrror",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
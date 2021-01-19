import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="odious",
    version="0.0.3",
    description="Optimizer comparisons",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/odious",
    author="microprediction",
    author_email="pcotton@intechinvestments.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["odious"],
    test_suite='pytest',
    tests_require=['pytest'],
    include_package_data=True,
    install_requires=["wheel","pathlib","numpy>=1.16.5","timemachines","pytest","microprediction"],
)

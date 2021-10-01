import re
from codecs import open
from os import path

from setuptools import setup

PACKAGE_NAME = "discord_slash_components_bridge"
HERE = path.abspath(path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

with open(path.join(HERE, PACKAGE_NAME, "const.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Damego",
    author_email="danyabatueff@gmail.com",
    description="Library for discord-components and discord-py-interactions(discord-slash).",
    include_package_data=True,
    install_requires=requirements,
    license="MIT License",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Damego/discord-py-slash-components-bridge",
    packages=["discord_slash_components_bridge"],
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
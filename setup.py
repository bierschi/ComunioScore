from setuptools import setup, find_packages

from ComunioScore import __version__, __author__, __email__, __license__

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", encoding='utf-8') as f:
    readme = f.read()

with open("CHANGELOG.rst") as f:
    changelog = f.read()

setup(
    name="ComunioScore",
    version=__version__,
    description="Maps the sofascore rating to comunio players",
    long_description=readme + "\n\n" + changelog,
    license=__license__,
    author=__author__,
    author_email=__email__,
    url="https://github.com/bierschi/ComunioScore",
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('/etc/systemd/system', ['service/ComunioScoreApp.service'])
    ],
    install_requires=required,
    keywords=["Comunio", "Sofascore", "Rating", "Score"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points={
        "console_scripts": [
            'ComunioScoreApp = ComunioScore.app:main'
        ],
    },
    zip_safe=False,
)

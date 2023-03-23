import os
from setuptools import setup, find_packages

# from piescope._version import __version__


def parse_requirements_file(filename):
    with open(filename) as fid:
        requires = [l.strip() for l in fid.readlines() if l]

    return requires


descr = """DeMarco lab openCLEM package."""

DISTNAME = 'openCLEM'
DESCRIPTION = 'Integrated correlative light-electron microscopy tool'
LONG_DESCRIPTION = descr
AUTHOR_EMAIL = 'David.Dierickx1@monash.edu'
MAINTAINERS = 'David Dierickx'
URL = 'https://github.com/DeMarcoLab/openCLEM'
DOWNLOAD_URL = 'https://github.com/DeMarcoLab/openCLEM'
# VERSION = __version__
PYTHON_VERSION = (3, 9)
INST_DEPENDENCIES = parse_requirements_file(
    'requirements.txt'
)

if __name__ == '__main__':
    setup(
        name=DISTNAME,
        # version=__version__,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=MAINTAINERS,
        author_email=AUTHOR_EMAIL,
        packages=find_packages(),
        install_requires=INST_DEPENDENCIES,
    )

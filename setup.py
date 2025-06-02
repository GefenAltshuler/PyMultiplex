from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PyMultiplex',
    version='1.1',
    author='Gaffner',
    author_email='gefen102@gmail.com',
    url="https://github.com/GefenAltshuler/PyMultiplex",
    packages=['PyMultiplex'],
    entry_points={
        'console_scripts': [
            'multiplex = PyMultiplex.__main__:main'
        ]
    },
    description='Transfer data across multiple virtual channels over a single socket connection using multiplexing',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
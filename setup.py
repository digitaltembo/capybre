from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='capybre',
    version='0.0.2',
    description='Python interface for Calibre\'s command line tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/digitaltembo/capybre',
    author='Nolan Hawkins',
    author_email='nolanhhawkins@gmail.com',
    license='MIT',
    packages=['capybre'],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=['nose'],
)

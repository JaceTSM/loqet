import setuptools


def load_long_description():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


setuptools.setup(
    name="loqet",
    version="0.0.3",
    author="Tim Murphy",
    author_email="jac3tssm@gmail.com",
    description="Local secrets manager in python",
    long_description=load_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/JaceTSM/loqet",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "cryptography",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "loq=loqet.loq_cli:loq_cli",
            "loqet=loqet.loqet_cli:loqet_cli",
        ],
    }
)

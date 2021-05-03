import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="loqet",
    version="0.0.1",
    author="Tim Murphy",
    author_email="jac3tssm@gmail.com",
    description="Local secrets manager in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JaceTSM/loqet",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
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

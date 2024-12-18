from setuptools import setup, find_packages

setup(
    name="automate_unsupervised_dataset_generation",                   # Package name
    version="0.5.0",                     # Version number
    author="Prakhar Gandhi",                  # Author's name
    author_email="gprakhar0@gmail.com",  # Author's email
    description="A brief description",   # Short description
    long_description=open("README.md").read(),  # Long description from README
    long_description_content_type="text/markdown",
    url="https://github.com/prakHr/automate-unsupervised-dataset-generation",  # URL of the project
    packages=find_packages(),            # Automatically discover modules
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",             # Minimum Python version
    install_requires=[                   # Dependencies
        "mpire",
        "playwright",
        "transformers",
        "torch",
        "torchvision",
        "hyperopt==0.2.5",
        "hpsklearn==0.1.0",
        "numpy==1.23",
        "languagemodels"
    ],
)

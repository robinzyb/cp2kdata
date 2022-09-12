import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Cp2kData",
    version="0.4.0",
    author="Yongbin Zhuang",
    author_email="robinzhuang@stu.xmu.edu.com",
    description="Small Package to Postprocessing Cp2k Output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robinzyb/cp2kdata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)"
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy >= 1.19.5",
        "scipy >= 1.5.4",
        "matplotlib >= 3.3.2",
        "ase >= 3.20.1",
        "dpdata",
        "click",
        "regex",
        "pytest",
        "pytest-cov"
  ],
   entry_points={
       'console_scripts': [
           'cp2kdata=cp2kdata.cli.cmd:cli'],
       'dpdata.plugins':[
           'cp2kdata/md = cp2kdata.dpdata_plugin:CP2KMDFormat'
           ]
       }
)

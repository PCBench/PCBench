from setuptools import setup, find_packages

setup(
    name='PCBench',
    version='1.0',
    author='PCBench routing team',
    description='Dataset and RL environment for PCB routing',
    url='https://github.com/PCBench/PCBench',
    python_requires='>=3.8, <4',
    packages=find_packages("."),
    install_requires=[
        'gymnasium==0.28.1',
        'scipy==1.10.1',
        'numpy==1.24.3',
    ]
)
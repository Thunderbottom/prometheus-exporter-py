from setuptools import setup

setup(
    name='prometheus-exporter',
    packages=['prometheus_exporter'],
    version='0.1',
    description='A wrapper for prometheus_client to simplify metrics generation for python applications',
    license='MIT',
    author='Chinmay D. Pai',
    author_email='chinmaydpai@gmail.com',
    url='https://github.com/Thunderbottom/prometheus-exporter-py',
    keywords=['prometheus', 'exporter', 'monitoring', 'wrapper'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Monitoring'
    ],
    install_requires=['prometheus_client'],
)

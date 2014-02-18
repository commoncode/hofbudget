from setuptools import setup, find_packages

setup(
    name='hoftbudget',
    version='0.0.1',
    description='Simple budgeter tool.',
    author='Gamaliel Chávez',
    author_email='gamaliel@commoncode.com.au',
    url='https://github.com/commoncode/hofbudget',
    keywords=['django', 'toggl', 'budget'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'requests'
    ]
)

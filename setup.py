from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-extras',
    version=version,
    description="Extension provides facilities to list resources that are not local",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Cezary Statkiewicz',
    author_email='cezary.statkiewicz@geo-solutions.it',
    url='http://www.geo-solutions.it/',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.extras'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        external_resource_list=ckanext.extras.plugin:ExternalResourceListPlugin

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan


        [nose.plugins]
        main = ckan.ckan_nose_plugin:CkanNose
    ''',

    # Translations
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)

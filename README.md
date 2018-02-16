
[![Build Status](https://travis-ci.org/geosolutions-it/ckanext-extras.svg?branch=master)](https://travis-ci.org/geosolutions-it/ckanext-extras)

# ckanext-extras

The ckanext-extras CKAN's extension provides `external_resource_list` action, which returns list of public resources, which are not local (are served by external service).

## Requirements

The ckanext-extras extension has been developed for CKAN 2.4.3 or later.

## Installation

1. Installing all the other extensions required

2. Activate your CKAN virtual environment, for example:

     `. /usr/lib/ckan/default/bin/activate`
     
3. Go into your CKAN path for extension (like /usr/lib/ckan/default/src):

    `git clone https://github.com/geosolutions-it/ckanext-extras.git`
    
    `cd ckanext-extras`
    
    `pip install -e .`

4. Add ``external_resource_list`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at ``/etc/ckan/default/production.ini``).


5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     `sudo service apache2 reload`

## Configuration

This extension uses `ckan.site_url` value to resolve if url is external. If url starts with local site value, it will be considered as local.

However, it may came to situation, that single site url is insufficient. For that case, you can add `ckanext.extras.local_sites` to config. This can be a string or list of strings with base urls, which should be considered as local.

Additionally, urls that starts with values from local sites, may be actually external (proxied from external sites). In that case, you can also set `ckanext.extras.external_sites`. 

To establish if url is external in such scenario, url will be checked with external sites first (if url starts with external site prefix, it will be considered external at this point), then with local sites (if url starts with local site prefix, it will be considered local). If none of those checks will provide result, url will eventually be considered as external.


### Example

Sample configuration:

```
ckan.site_url = http://public.address

ckanext.extras.local_sites =
    http://localhost
    http://127.0.0.1

ckanext.extras.external_sites = 
    http://localhost/proxied
    http://public.address/remote/

```

url | is external
--- | ---
`http://public.address/index` | No
`http://public.address/remote/index` | Yes
`http://localhost/resource/001` | No
`http://localhost/proxied/resource/001` | Yes


## Development Installation

To install `ckanext-extras` for development, activate your CKAN virtualenv and do:

	git clone https://github.com/geosolutions-it/ckanext-extras.git

	cd ckanext-extras

	python setup.py develop


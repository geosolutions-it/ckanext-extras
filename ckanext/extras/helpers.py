#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan.lib.base import config
from sqlalchemy.sql.expression import not_, or_, and_

SITE_URL = config['ckan.site_url']
LOCAL_SITES = []
EXTERNAL_SITES = []


def get_local_sites():
    global LOCAL_SITES
    out = [SITE_URL]
    _local_sites = config.get('ckanext.extras.local_sites')
    if _local_sites:
        out.extend([u.strip()
                    for u in _local_sites.replace('\n', ' ')
                                         .split(' ')
                    if u.strip()])
    LOCAL_SITES = tuple(out)


def get_external_sites():
    global EXTERNAL_SITES
    out = []
    _external_sites = config.get('ckanext.extras.external_sites')
    if _external_sites:
        out.extend([u.strip()
                    for u in _external_sites.replace('\n', ' ')
                                         .split(' ')
                    if u.strip()])
    EXTERNAL_SITES = tuple(out)


def init_sites():
    get_local_sites()
    get_external_sites()


def is_local_site(url):
    # check explicitly external sites first
    if url.startswith(EXTERNAL_SITES):
        return False
    # check if it's not local site
    return url.startswith(LOCAL_SITES)


def get_external_resources(session, model):

    r = model.Resource
    p = model.Package

    # 2.5 uses sqlalchemy 0.9+
    if hasattr(r.url, 'startswith'):
        _exclude = [r.url.startswith(item) for item in LOCAL_SITES]
        exclude_local_sites = or_(*_exclude)
        q = session.query(r, p)\
                   .join(p) \
                   .filter(p.state == 'active') \
                   .filter(p.private.is_(False)) \
                   .filter(r.state == 'active') \
                   .filter(and_(or_(r.url.startswith('http://'),
                                r.url.startswith('https://')),
                           not_(exclude_local_sites)))\
                   .order_by(r.url)

    else:

        _exclude = [r.url.ilike('{}%'.format(item)) for item in LOCAL_SITES]
        exclude_local_sites = or_(*_exclude)
        q = session.query(r, p)\
                   .join(p) \
                   .filter(p.state == 'active') \
                   .filter(p.private.is_(False)) \
                   .filter(r.state == 'active') \
                   .filter(and_(or_(r.url.ilike('http://%'),
                                    r.url.ilike('https://%')),
                                not_(exclude_local_sites)))\
                   .order_by(r.url)
    return q

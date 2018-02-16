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


init_sites()

def is_local_site(url):
    # check explicitly external sites first
    if url.startswith(EXTERNAL_SITES):
        return False
    # check if it's not local site
    return url.startswith(LOCAL_SITES)


def get_external_resources(session, model):

    r = model.Resource
    p = model.Package

    base_q = session.query(r.id, r.url, r.name, p.id, p.title)\
                    .join(p) \
                    .filter(p.state == 'active') \
                    .filter(p.private.is_(False)) \
                    .filter(r.state == 'active') \

    # 2.5 uses sqlalchemy 0.9+
    if hasattr(r.url, 'startswith'):
       
        _filter = [r.url.startswith(item) for item in EXTERNAL_SITES]
        _exclude = [r.url.startswith(item) for item in LOCAL_SITES]
        q = base_q
        local_q = base_q

        if _filter:
            local_q = local_q.filter(not_(or_(*_filter)))
        if _exclude:
            local_q = local_q.filter(or_(*_exclude))
        q = base_q.except_(local_q)


    else:
        # todo: subq
        _filter = [r.url.ilike('{}%'.format(item)) for item in EXTERNAL_SITES]
        _exclude = [r.url.ilike('{}%'.format(item)) for item in LOCAL_SITES]
        q = base_q
        local_q = base_q

        if _filter:
            local_q = local_q.filter(not_(or_(*_filter)))
        if _exclude:
            local_q = local_q.filter(or_(*_exclude))
        q = base_q.except_(local_q)

    return q.order_by(r.url)

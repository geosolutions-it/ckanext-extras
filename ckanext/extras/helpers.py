#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan.lib.base import config
from sqlalchemy.sql.expression import not_, or_, and_

_SITES_INITED = False
SITE_URL = config['ckan.site_url']
LOCAL_SITES = []
EXTERNAL_SITES = []
FILTER_KNOWN_NON_LOCAL = ('http://', 'https://', '/',)

def get_local_sites(initial=None):
    global LOCAL_SITES
    # local site and non-http paths (which are local anyway)
    out = [SITE_URL, '/']
    if initial is not None:
        out.extend(initial)
    else:
        out.extend(LOCAL_SITES)
    _local_sites = config.get('ckanext.extras.local_sites')
    if _local_sites:
        out.extend([u.strip()
                    for u in _local_sites.replace('\n', ' ')
                                         .strip()
                                         .split(' ')
                    if u.strip()])
    LOCAL_SITES = tuple(set(out))


def get_external_sites(initial=None):
    global EXTERNAL_SITES
    out = []
    if initial is not None:
        out.extend(initial)
    else:
        out.extend(EXTERNAL_SITES)
    _external_sites = config.get('ckanext.extras.external_sites')
    if _external_sites:
        out.extend([u.strip()
                    for u in _external_sites.replace('\n', ' ')
                                         .split(' ')
                    if u.strip()])
    EXTERNAL_SITES = tuple(set(out))


def init_sites(internal=None, external=None):
    global _SITES_INITED
    force = internal is not None or external is not None
    if _SITES_INITED and not force:
        return
    get_local_sites(internal)
    get_external_sites(external)
    _SITES_INITED = True


init_sites()

def is_local_site(url):
    # check explicitly external sites first
    if url.startswith(EXTERNAL_SITES):
        return False
    # check if it's not local site
    return url.startswith(LOCAL_SITES) or\
        not url.startswith(FILTER_KNOWN_NON_LOCAL)


def get_external_resources(session, model):

    r = model.Resource
    p = model.Package

    base_q = session.query(r.id, r.url, r.name, p.id, p.title)\
                    .join(p) \
                    .filter(p.state == 'active') \
                    .filter(p.private.is_(False)) \
                    .filter(r.state == 'active')

    local_q = base_q
    # 2.5 uses sqlalchemy 0.9+
    if hasattr(r.url, 'startswith'):
       
        _filter = [r.url.startswith(item) for item in EXTERNAL_SITES]
        _exclude = [r.url.startswith(item) for item in LOCAL_SITES]
        _known_local = [r.url.startswith(item) for item in FILTER_KNOWN_NON_LOCAL]

        if _filter:
            local_q = local_q.filter(not_(or_(*_filter)))
        if _exclude:
            local_q = local_q.filter(or_(*_exclude))


    else:
        # todo: subq
        _filter = [r.url.ilike('{}%'.format(item)) for item in EXTERNAL_SITES]
        _exclude = [r.url.ilike('{}%'.format(item)) for item in LOCAL_SITES]
        _known_local = [r.url.ilike('{}%'.format(item)) for item in FILTER_KNOWN_NON_LOCAL]

        if _filter:
            local_q = local_q.filter(not_(or_(*_filter)))
        if _exclude:
            local_q = local_q.filter(or_(*_exclude))
   
    q = base_q.filter(or_(*_known_local)).except_(local_q)
    return q.order_by(r.url)

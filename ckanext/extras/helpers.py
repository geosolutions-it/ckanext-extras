#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan.lib.base import config
from ckan import plugins
from ckan.plugins import toolkit
from sqlalchemy.sql.expression import not_, or_, and_

def get_external_resources(session, model, ):

    site_url = config.get('ckan.site_url')
    r = model.Resource
    p = model.Package

    # 2.5 uses sqlalchemy 0.9+
    if hasattr(r.url, 'startsWith'):
        q = session.query(r, p)\
             .join(p) \
             .filter(p.state == 'active') \
             .filter(p.private == False) \
             .filter(r.state == 'active') \
             .filter(not_(or_(r.url.startsWith(site_url),
                               r.url.startsWith('/'))))\
             .order_by(r.url)

    else:
        q = session.query(r, p)\
             .join(p) \
             .filter(p.state == 'active') \
             .filter(p.private == False) \
             .filter(r.state == 'active') \
             .filter(not_(or_(r.url.like('{}%'.format(site_url)),
                              r.url.like('/%'))))\
             .order_by(r.url)
    return q

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan.lib.base import config
from ckan import plugins
from ckan.plugins import toolkit
from sqlalchemy.sql.expression import not_, or_, and_

SITE_URL = config['ckan.site_url']

def get_external_resources(session, model, ):

    r = model.Resource
    p = model.Package

    # 2.5 uses sqlalchemy 0.9+
    if hasattr(r.url, 'startswith'):
        q = session.query(r, p)\
             .join(p) \
             .filter(p.state == 'active') \
             .filter(p.private == False) \
             .filter(r.state == 'active') \
             .filter(and_(or_(r.url.startswith('http://'),
                              r.url.startswith('https://')),
                         not_(r.url.startswith(SITE_URL))))\
             .order_by(r.url)

    else:
        q = session.query(r, p)\
             .join(p) \
             .filter(p.state == 'active') \
             .filter(p.private == False) \
             .filter(r.state == 'active') \
             .filter(and_(or_(r.url.ilike('http://%'),
                              r.url.ilike('https://%')),
                         not_(r.url.ilike('{}%'.format(SITE_URL)))))\
             .order_by(r.url)
    return q

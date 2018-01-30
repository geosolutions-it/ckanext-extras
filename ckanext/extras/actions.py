#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan.logic import check_access, side_effect_free
from ckan.plugins import toolkit as t
from ckanext.extras import helpers as h


DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0

@side_effect_free
def external_resource_list(context, data_dict):
    """
    Return list of resources that are not local
    
    The list is sorted by url (a-z order).

    :param limit: if provided, the list of resources will paged by 
        ``limit`` per page, otherwise default {} will be used.
    :type limit: int

    :param offset: start returning packages from specified item. If not
        provided, 0 will be used
    :type offset: int

    :rtype: list of dictionaries with keys: name, url, dataset, dataset_url

    """.format(DEFAULT_LIMIT)

    s = context['session']
    m = context['model']
    q = h.get_external_resources(s, m)

    limit = int(data_dict.get('limit') or DEFAULT_LIMIT)
    offset = int(data_dict.get('offset') or DEFAULT_OFFSET)
    
    count = q.count()
    q = q.limit(limit).offset(offset)
    
    data = []
    get_res = t.get_action('resource_show')
    get_pkg = t.get_action('package_show')

    for item in q:

        res, pkg = item

        item_dict = {'dataset': { 'id': pkg.id,
                                  'title': pkg.title,
                                  'url': t.url_for('dataset_read',
                                                   id=pkg.id,
                                                   qualified=True)},
                     'url': res.url,
                     'id': res.id}

        data.append(item_dict)
    out = {'count': count,
           'limit': limit,
           'offset': offset,
           'data': data}

    return out

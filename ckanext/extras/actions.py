#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan.logic import check_access, side_effect_free
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
    q.limit(data_dict.get('limit') or DEFAULT_LIMIT)
    q.offset(data_dict.get('offset') or DEFAULT_OFFSET)

    out = [{'dataset': item[1].title,
             'dataset_url': item[1].url,
             'name': item[0].name,
             'url': item[0].url} for item in q]
    return out

    

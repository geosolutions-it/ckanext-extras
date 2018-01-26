#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ckan import plugins
from ckan.plugins import toolkit
from ckanext.extras import actions

log = logging.getLogger(__name__)

class ExternalResourceListPlugin(plugins.SingletonPlugin):
    '''
    List of external resources exposed as external_resource_list
    '''

    plugins.implements(plugins.IActions)


    def get_actions(self):
        return {'external_resource_list': actions.external_resource_list}

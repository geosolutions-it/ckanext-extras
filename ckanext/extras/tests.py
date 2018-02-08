#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from ckan import model
from ckan.lib.base import config
from ckan.model.meta import Session as session
from ckan.tests.helpers import call_action
from ckan.lib.helpers import url_is_local


SITE_URL = config['ckan.site_url']

def url_is_external(val):
    return not url_is_local(val)


class ExternalResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        self.p = {'title': 'Test package',
                  'name': 'test-package',
                  'resources': [{'id': 'res01',
                                 'url': '{}/111.zip'.format(SITE_URL)},
                                {'id': 'res02',
                                 'url': '{}/local/222'.format(SITE_URL)},
                                {'id': 'res03',
                                 'url': 'http://external.server/test.res'},
                               ],
                  'url': 'http://test.server/'
             }
        self.ctx = {'ignore_auth': True,
                    'model': model,
                    'session': session,
                    'user': 'user'}

        out = call_action('package_create', context=self.ctx, **self.p)

    def tearDown(self):
        model.repo.rebuild_db()

    def test_action(self):
        out = call_action('external_resource_list', context=self.ctx)
        self.assertEqual(out['data'][0]['url'], self.p['resources'][2]['url'])

        resources = []
        for idx in xrange(0, 100):
            if idx % 2 == 0:
                resources.append({'id': 'res{}'.format(idx),
                                  'url': 'file{:2d}.bin'.format(idx)})
            else:
                resources.append({'id': 'res{}'.format(idx),
                                  'url': 'http://external/server/{:02d}'.format(idx)})

        p = self.p.copy()
        p.update({'title': 'test package 2',
                  'name': 'test-package-2'})
        p['resources'] = resources

        call_action('package_create', context=self.ctx, **p)
        out = call_action('external_resource_list', context=self.ctx, limit=10, offset=2)

        self.assertEqual(out.get('count'), 50)
        self.assertEqual(out.get('limit'), 10)
        self.assertEqual(out.get('offset'), 2)

        self.assertEqual(len(out.get('data')), 10)
        self.assertEqual(out['data'][0]['url'], resources[5]['url'])

    def test_external_urls(self):
        """
        Check if all resources retruyned from api are external.
        Also, check if resource urls are recognized as external.

        """
        out = call_action('external_resource_list', context=self.ctx)
        self.assertTrue(len(out['data'])> 0)
        for urlx in out['data']:
            url = urlx['url']
            self.assertTrue(url_is_external(url))

        pkg = call_action('package_show', context=self.ctx, name_or_id=self.p['name'])
        self.assertTrue(pkg)
        self.assertTrue(len(pkg['resources']) == 3)
        for res in pkg['resources']:
            # known external
            if res['id'] == 'res03':
                self.assertTrue(url_is_external(res['url']))
            else:
                self.assertTrue(url_is_local(res['url']))

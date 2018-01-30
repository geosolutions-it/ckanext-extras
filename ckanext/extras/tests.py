#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from ckan import model
from ckan.model.meta import Session as session
from ckan.tests.helpers import call_action


class ExternalResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        self.p = {'title': 'Test package',
             'name': 'test-package',
             'resources': [{'id': 'res01',
                            'url': '111.zip'},
                            {'id': 'res02',
                             'url': '/local/222'},
                            {'id': 'res03',
                             'url': 'http://external.server/test.res'},
                           ],
             'url': 'http://test.server/'

             }
        self.ctx = {'ignore_auth': True,
                    'model': model,
                    'session': session,
                    'user': 'user'}

        call_action('package_create', context=self.ctx, **self.p)

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

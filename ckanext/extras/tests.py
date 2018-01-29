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
                            'url': 'http://test.server/111'},
                            {'id': 'res02',
                             'url': '/local/222'}
                           ]
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
        self.assertEqual(out[0]['url'], self.p['resources'][0]['url'])
        resources = [{'id': 'res{}'.format(idx), 'url': 'http://external/server/{}'.format(idx)} for idx in range(0, 100)]

        p = self.p.copy()
        p.update({'title': 'test package 2',
                  'name': 'test-package-2'})
        p['resources'] = resources

        call_action('package_create', context=self.ctx, **p)

        out = call_action('external_resource_list', context=self.ctx, limit=10)
        self.assertEqual(len(out), 10)
        self.assertEqual(out[0]['url'], resources[0]['url'])

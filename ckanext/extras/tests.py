#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from ckan import model
from ckan.lib.base import config
from ckan.model.meta import Session as session
from ckan.model import Resource
from ckan.tests.helpers import call_action, reset_db, change_config
from ckanext.extras.helpers import init_sites, is_local_site, LOCAL_SITES, EXTERNAL_SITES

SITE_URL = config['ckan.site_url']
OTHER_LOCAL_URL = 'http://some.other.server'
OTHER_EXTERNAL_URL = 'http://some.other.server/proxied'

config['ckanext.extras.local_sites'] =\
    'http://localhost {}'.format(OTHER_LOCAL_URL)

config['ckanext.extras.external_sites'] =\
    'http://completely.different.host {}'.format(OTHER_EXTERNAL_URL)


# update with new config
init_sites(internal=[], external=[])

# quick wrapper around url detection
def url_is_external(val):
    return not is_local_site(val)


class ExternalResourceTestCase(unittest.TestCase):

    def setUp(self):
        reset_db()
        self.p = {'title': 'Test package',
                  'name': 'test-package',
                  'resources': [{'id': 'local01',
                                 'url': '{}/111.zip'.format(SITE_URL)},
                                {'id': 'local02',
                                 'url': '{}/local/222'.format(SITE_URL)},
                                {'id': 'external03',
                                 'url': 'http://external.server/test.res'},
                                {'id': 'local04',
                                 'url': '{}/local/04'.format(OTHER_LOCAL_URL)},
                                {'id': 'external05',
                                 'url': '{}/remote/05'.format(OTHER_EXTERNAL_URL)},
                                {'id': 'local06',
                                 'url': 'local/06'}
                                ],
                  'url': 'http://test.server/'
                  }
        self.ctx = {'ignore_auth': True,
                    'model': model,
                    'session': session,
                    'for_edit': True,
                    'user': 'user'}

        p = call_action('package_create', context=self.ctx, **self.p)
        r = session.query(Resource).filter_by(package_id=p['id'], name='local06')
        r.url = 'local/06'
        session.flush()

    def tearDown(self):
        reset_db()

    def test_action(self):
        out = call_action('external_resource_list', context=self.ctx)
        self.assertEqual(out['count'], 2, out)
        for item in out['data']:
            self.assertTrue(item['id'].startswith('external'), item)

        resources = []
        for idx in xrange(0, 100):
            if idx % 2 == 0:
                resources.append({'id': 'res{}'.format(idx),
                                  'url': 'http://localhost/file{:2d}.bin'.format(idx)})
            else:
                resources.append({'id': 'res{}'.format(idx),
                                  'url': ('http://external/'
                                          'server/{:02d}').format(idx)})

        p = self.p.copy()
        p.update({'title': 'test package 2',
                  'name': 'test-package-2'})
        p['resources'] = resources

        call_action('package_create', context=self.ctx, **p)
        out = call_action('external_resource_list',
                          context=self.ctx,
                          limit=10,
                          offset=2)

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
        self.assertTrue(len(out['data']) > 0)
        for urlx in out['data']:
            url = urlx['url']
            self.assertTrue(url_is_external(url))

        pkg = call_action('package_show',
                          context=self.ctx,
                          name_or_id=self.p['name'])
        self.assertTrue(pkg)
        self.assertTrue(len(pkg['resources']) == len(self.p['resources']))
        external_count = 0
        for res in pkg['resources']:
            # known external
            if res['id'].startswith('external'):
                self.assertTrue(url_is_external(res['url']), (res['id'], res['url']))
                if res['id'] == 'external05':
                    self.assertTrue(res['url'].startswith(OTHER_LOCAL_URL))
                external_count += 1
            else:
                self.assertTrue(not url_is_external(res['url']), res)
        self.assertEqual(external_count, 2)

    @change_config('ckanext.extras.external_sites', '')
    def test_external_urls_no_exceptions(self):
        """
        Check if all resources retruyned from api are external.
        Also, check if resource urls are recognized as external.

        """
        init_sites(external=[])

        out = call_action('external_resource_list', context=self.ctx)
        self.assertTrue(len(out['data']) > 0)
        for urlx in out['data']:
            url = urlx['url']
            self.assertTrue(url_is_external(url))

        pkg = call_action('package_show',
                          context=self.ctx,
                          name_or_id=self.p['name'])
        self.assertTrue(pkg)
        self.assertTrue(len(pkg['resources']) == len(self.p['resources']))
        external_count = 0
        for res in pkg['resources']:
            # known external - 03, because prefix is exteral
            if res['id'] == 'external03':
                self.assertTrue(url_is_external(res['url']), (res['id'], res['url']))
                external_count += 1
            else:
                # external05 is local, because it's not excluded in external_sites now
                self.assertTrue(not url_is_external(res['url']), (res['id'], res['url']))
        self.assertEqual(external_count, 1)

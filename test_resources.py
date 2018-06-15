#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import urllib
import requests
from pprint import pprint

def fetch(url):
    urls = [url]
    offset = 0
    count = 0
    while urls:
        url = urls.pop(0)
        r = requests.get(url, {'offset': offset})
        data = r.json()
        if offset == 0:
            print('total items', data['result']['count'])
        if not data['result']['data']:
            break
        count += len(data['result']['data'])
        if count <= data['result']['count']:
            offset += 50
            urls.append(url)
        for idx, res in enumerate(data['result']['data']):
            if not res['url'].startswith(('http', '/')):
                print('   bad filename at', url, offset, offset + idx)
                print('   ', res['url'])
                print('   ', res)

def main():
    url = sys.argv[1]

    out = fetch(url)


if __name__ == '__main__':
    main()


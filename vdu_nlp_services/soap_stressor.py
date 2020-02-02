#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zeep import Client
from hashlib import sha1
import re

_stress_re = re.compile(r'\d+. ([^\( \)]+) \(([^\)]+)?\)')

_stress_map = {
    '&#x0300;': '`',
    '&#x0301;': '^',
    '&#x0303;': '~'
}

_stress_text_cache = {}

def get_stress_text_cache(h):
    return _stress_text_cache[h]

def set_stress_text_cache(h, result):
    _stress_text_cache[h] = result

def get_request_body(text, version='8.0'):  
    request_body = {
        'in':text,
        'Versija':version,
        'WP':''
    }
    return request_body

def get_hash_from_request_body(request_body):
    return int(sha1( repr(sorted(frozenset(request_body.items()))).encode("utf-8") ).hexdigest(), 16) % (10 ** 16)

def stress_text(text, version='8.0'):
    request_body = get_request_body(text, version='8.0')
    h = get_hash_from_request_body(request_body)

    try:
        result = get_stress_text_cache(h)
    except KeyError:

        client = Client('http://donelaitis.vdu.lt/Kirtis/KServisas.php?wsdl')
        result = client.service.kirciuok(request_body)

        if result['Klaida'] and result['Klaida'] == u'Per daug žodžių, sumažinkite žodžių kiekį':
            splits = re.sub(r'([a-z][\?!])(\s+[A-Z])', r'\g<1>\n\g<2>', text, count=1).split('\n')
            index = int(len(splits)/2)
            splits_a = ' '.join(splits[:index])
            splits_b = ' '.join(splits[index:])
            tmp_result = ''
            for split in [splits_a, splits_b]:
                tmp_result += stress_text(split, version)
            result['out'] = tmp_result
            result['Klaida'] = None
            result['Info'] = None

        for k,v in _stress_map.items():
            result['out'] = result['out'].replace(k, v)

        assert (result['Info'] == None)
        assert (result['Klaida'] == None)

        set_stress_text_cache(h, result)

    return result['out']
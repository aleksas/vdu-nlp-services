#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zeep import Client
from hashlib import sha1

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

        for k,v in _stress_map.items():
            result['out'] = result['out'].replace(k, v)

        assert (result['Info'] == None)
        assert (result['Klaida'] == None)

        set_stress_text_cache(h, result)

    return result['out']

if __name__ == '__main__':
    print (stress_text('Laba diena draugai! Kaip jums sekasi? Vienas, du, trys.'))
    print (stress_text('namo'))
    print (stress_text('Šioje vietoje trūksta namo!'))
    print (stress_text('Einam namo!'))
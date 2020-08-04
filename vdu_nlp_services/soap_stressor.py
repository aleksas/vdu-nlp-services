#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zeep import Client
from hashlib import sha1
import re

_stress_re = re.compile(r'\d+. ([^\( \)]+) \((.+)?\)')

_stress_map = {
    '&#x0300;': '`',
    '&#x0301;': '^',
    '&#x0303;': '~'
}
_stress_signs = ''.join([v for v in _stress_map.values()])

stress_tag_replacements = {
    'Vt(ev).neįvardž.': ['Vt(ev).', 'neįvardž.'],
    'Vt(ev).nesngr.': ['Vt(ev).', 'nesngr.']
}

stress_verb_form_tag_replacements = {
    'dlv.': ['vksm.', 'dlv.'],
    'padlv.': ['vksm.', 'padlv.'],
    'psdlv.': ['vksm.', 'psdlv.'],
    'būdn.': ['vksm.', 'būdn.']
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

def fix_stress_tags(stress_tags):
    for i, tag in enumerate(stress_tags):
        tag_replacement = None

        if tag in stress_tag_replacements:
            tag_replacement = stress_tag_replacements[tag]
        elif i == 0 and tag in stress_verb_form_tag_replacements:
            tag_replacement = stress_verb_form_tag_replacements[tag]

        if tag_replacement:
            if isinstance(tag_replacement, list):
                for replacement in tag_replacement:
                    yield replacement
            else:
                yield tag_replacement
        else:
            yield tag

def stress_word(word, version='8.0'):
    res = stress_text(word.strip(), version).splitlines()

    for line in res:
        m = _stress_re.match(line)
        if m:
            stressed_word = m.group(1)
            stress_tags = m.group(2).split(' ') if m.group(2) else []
            yield stressed_word, fix_stress_tags(stress_tags)
        else:
            if not set(line).difference(set(line + _stress_signs)):
                yield line, []
            else:
                yield word, []

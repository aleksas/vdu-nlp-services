#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .morphological_analyzer import analyze_text
from .soap_stressor import stress_text
import re

_word_stress_option_cache = {}
_stress_re = re.compile(r'\d+. ([^\( \)]+) \((.+)?\)')
_stress_re_ex = re.compile(r'[^\( \)]+')

_morph2opt_same = [
    u'V.', u'K.', u'G.', u'N.', u'Vt.', u'Įn.', u'Š.',
    u'jst.', u'vksm.', u'sktv.', u'dlv.', 
    u'sngr.', u'tiesiog. n.', u'nelygin. l.',
    u'įvardž.', u'neįvardž.',
    u'sngr.', u'nesngr.',
    u'reik.',
    u'dll.', 
    u'būdn.',
    u'kuopin.',
    u'dvisk.',
    u'idAA'
]

_morph2opt_missing = [
    u'teig.', u'neig.', u'teig',
    u'aukšt. l.', u'aukšč. l.', u'aukštėl. l.',
    u'sutr.', u'akronim.', u'dvisk.',
    u'rom. sk.',
    u'tar. n.', u'liep. n.',
    u'daugin.',
    u'idPS', #post scriptum
    u'nežinomas'
]

_morph2opt = {
    u'mot. g.': u'mot.gim.', u'vyr. g.': u'vyr.gim.', u'bev. g.': u'bevrd.gim.', u'bendr. g.': u'bendr.gim.',
    u'vns.': u'vnsk.', u'dgs.': u'dgsk.',
    u'dkt.': u'dktv.', u'bdv.': u'bdvr.', u'prv.': u'prvks.', u'įv.': u'įvrd.',
    u'bendr.': [u'vksm.', u'bendr.'],
    u'pusd.': u'psdlv.',
    u'prl.': u'prln.', u'idprl.': u'prln.',
    u'pad.': u'padlv.',
    u'jng.': u'jngt.', u'idjng.': u'jngt.',
    u'išt.': u'ištk.',
    u'es. l.': u'esam.l.', u'būt. l.': u'būt.l.', u'būt. k. l.': u'būt.kart.l.', u'būt. d. l.': u'būt.d.l.', u'būs. l.': u'būs.l.',
    u'1 asm.': u'Iasm.', u'2 asm.': u'IIasm.', u'3 asm.': u'IIIasm.',
    u'kiek.': u'kiekin.', u'kelint.' : u'kelintin.',    
    u'veik. r': u'veik.r.', u'neveik. r': u'neveik.r.', u'veik. r.': u'veik.r.', u'neveik. r.': u'neveik.r.',
    u'tikr. dkt.': [u'dktv.', u'T.']
}

_morph2opt.update( {k:k for k in _morph2opt_same} ) 
_morph2opt.update( {k:k for k in _morph2opt_missing} ) 

def get_cached_word_stress_options(word):
    return _word_stress_option_cache[word]

def set_cached_word_stress_options(word, options):
    _word_stress_option_cache[word] = options

def get_word_stress_options(word):
    if word:
        try:
            return get_cached_word_stress_options(word)
        except KeyError:
            raw_stress_options = filter(None, stress_text(word).split('\n'))
            stress_options = []
            max_opts = 0

            for rso in raw_stress_options:
                m = _stress_re.match(rso)
                if m:
                    stressed_word = m.group(1)
                    grammar_specs = m.group(2).split(' ') if m.group(2) else []
                    stress_options.append( (stressed_word, grammar_specs) )
                else:
                    if word == rso or ' ' not in rso:
                        stress_options.append( (rso, []) )
                        max_opts = 1
                    else:
                        raise Exception()

            if max_opts and len(stress_options) > max_opts:
                raise Exception()

            set_cached_word_stress_options(word, stress_options)

            return stress_options

def _stress_selector(annotated_type, stress_options):
    annotated_type_set = set([v for k in annotated_type.split(', ') for v in (_morph2opt[k] if isinstance(_morph2opt[k], list) else [_morph2opt[k]])])
    stressed_words = {}
    for stress in stress_options:
        stress_type = stress[1]
        stress_type_set = set(stress_type)
        intersection = annotated_type_set.intersection(stress_type_set)
        intersection_size = len(intersection)
        stressed_words[stress[0]] = intersection_size if stress[0] not in stressed_words else max(stressed_words[stress[0]], intersection_size)
    
    if len(set(stressed_words.keys())) == 0:
        return None
    else:
        sorted_stressed_words = sorted(stressed_words.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_stressed_words[0]

def fused_stress_replacements(text, exceptions=None, stress_selector=_stress_selector):
    _, augmented_elements = analyze_text(text, exceptions=exceptions)
    replacements = {}

    for i, element in enumerate(augmented_elements):
        if 'word' in element:
            stress_options = get_word_stress_options(element['word'])
            selected_stress = stress_selector(element['type'], stress_options)
            if selected_stress:
                replacements[i] = selected_stress[0]
            else:
                replacements[i] = element['word']
    return replacements, augmented_elements

def rebuild_text(augmented_elements, replacements=None):
    text = u''
    mappings = []
    for i, element in enumerate(augmented_elements):
        if 'word' in element:
            if replacements and i in replacements:
                mappings.append( (element['span'], (len(text), len(text) + len(replacements[i]))) )
                text += replacements[i]
            else:
                text += element['word']
        elif 'number' in element:
            text += str(element['number'])
        elif 'other' in element:
            text += str(element['other'])
        else:
            raise NotImplementedError()
    
    return text, mappings

def fused_stress_text(text, exceptions=None):
    replacements, augmented_elements = fused_stress_replacements(text, exceptions)
    rebuilt_text, mappings = rebuild_text(augmented_elements, replacements)
    return rebuilt_text, mappings

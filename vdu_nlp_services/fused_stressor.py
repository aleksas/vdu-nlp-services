from morphological_analyzer import analyze_text
from soap_stressor import stress_text
import re

_word_stress_option_cache = {}
_stress_re = re.compile(r'\d+. ([^\( \)]+) \(([^\)]+)?\)')
_stress_re_ex = re.compile(r'[^\( \)]+')

_morph2opt_same = [
    'V.', 'K.', 'G.', 'N.', 'Vt.', 'Įn.', 'Š.',
    'jst.', 'vksm.', 'sktv.', 'dlv.', 
    'sngr.', 'tiesiog. n.',  'nelygin. l.',
    'įvardž.', 'neįvardž.',
    'sngr.', 'nesngr.',
    'reik.',
    'dll.', 
    'būdn.',
    'kuopin.',
    'dvisk.',
    'idAA'
]

_morph2opt_missing = [
    'teig.', 'neig.', 'teig',
    'aukšt. l.', 'aukšč. l.', 'aukštėl. l.',
    'sutr.', 'akronim.','dvisk.',
    'rom. sk.',
    'tar. n.', 'liep. n.',
    'daugin.',
    'idPS', #post scritum
    'nežinomas'
]

_morph2opt = {
    'mot. g.': 'mot.gim.', 'vyr. g.': 'vyr.gim.', 'bev. g.':'bevrd.gim.', 'bendr. g.':'bendr.gim.',
    'vns.': 'vnsk.', 'dgs.': 'dgsk.',
    'dkt.': 'dktv.', 'bdv.': 'bdvr.', 'prv.': 'prvks.', 'įv.': 'įvrd.',
    'bendr.': ['vksm.', 'bendr.'],
    'pusd.': 'psdlv.',
    'prl.': 'prln.', 'idprl.': 'prln.',
    'pad.': 'padlv.',
    'jng.': 'jngt.', 'idjng.': 'jngt.',
    'išt.':'ištk.',
    'es. l.': 'esam.l.', 'būt. l.':'būt.l.', 'būt. k. l.': 'būt.kart.l.', 'būt. d. l.':'būt.d.l.', 'būs. l.':'būs.l.',
    '1 asm.': 'Iasm.', '2 asm.': 'IIasm.', '3 asm.': 'IIIasm.',
    'kiek.': 'kiekin.', 'kelint.' : 'kelintin.',    
    'veik. r': 'veik.r.', 'neveik. r': 'neveik.r.', 'veik. r.': 'veik.r.', 'neveik. r.': 'neveik.r.',
    'tikr. dkt.': ['dktv.', 'T.'],

    **{k:k for k in _morph2opt_same},
    **{k:k for k in _morph2opt_missing}
}

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

def localize_stressed_text(stressed_text, augmented_elemetns):
    offset = 0
    res = {}
    for i, ae in enumerate(augmented_elemetns):
        if 'word' in ae:
            pattern = ''.join( [ l + r'[`^~]?' for l in ae['word'] ] )
            m = re.search(pattern, stressed_text[offset:])
            if m:
                res[i] = m.group(0) #(m.span()[0] + offset, m.span()[1] + offset)
                offset += m.span()[1]
            else:
                raise Exception()
        elif 'number' in ae:
            m = re.search(ae['number'], stressed_text[offset:])
            if m:
                offset += m.span()[1]
            else:
                raise Exception()

    return res

def fused_stress_replacents(text, exceptions=None, stress_selector=_stress_selector):
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
    for i, element in enumerate(augmented_elements):
        if 'word' in element:
            if replacements and i in replacements:
                text += replacements[i]
            else:
                text += element['word']
        elif 'number' in element:
            text += str(element['number'])
        elif 'other' in element:
            text += str(element['other'])
        else:
            raise NotImplementedError()
    
    return text

def fused_stress_text(text, exceptions=None):
    replacements, augmented_elements = fused_stress_replacents(text, exceptions)
    return rebuild_text(augmented_elements, replacements)

def compare_replacements(replacements_maps):
    comparison_replacements = {}
    has_inequalities = False
    keys = set([])
    for replacements in replacements_maps:
        keys = keys.union(set(replacements.keys()))
    
    for k in keys:
        equal = True
        value = None
        for replacements in replacements_maps:
            if k not in replacements:
                equal = False
                break
            if not value:
                value = replacements[k]
            if value != replacements[k]:
                equal = False
                break

        if equal:
            comparison_replacements[k] = value
        else:
            has_inequalities = True
            comparison_replacements[k] = '|| ' + ' <> '.join([(replacements[k] if k in replacements else ' ') for replacements in replacements_maps ]) + ' ||'
    
    return comparison_replacements, has_inequalities

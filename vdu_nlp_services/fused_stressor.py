from morphological_analyzer import analyze_text
from soap_stressor import stress_text
import re
import sqlite3

_word_stress_option_cache = {}
_stress_re = re.compile(r'\d+. ([^\( )]+) \(([^\)]+)?\)')

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
    'dvisk.'
]

_morph2opt_missing = [
    'teig.', 'neig.', 'teig',
    'aukšt. l.', 'aukšč. l.',
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
    'veik. r': 'veik.r.', 'neveik. r': 'neveik.r.', 'veik. r.': 'veik.r.',
    'tikr. dkt.': ['dktv.', 'T.'],

    **{k:k for k in _morph2opt_same},
    **{k:k for k in _morph2opt_missing}
}

def get_word_stress_options(word):
    if word not in _word_stress_option_cache:
        raw_stress_options = filter(None, stress_text(word).split('\n'))
        stress_options = []
        for rso in raw_stress_options:
            m = _stress_re.match(rso)
            if m:
                stressed_word = m.group(1)
                grammar_specs = m.group(2).split(' ') if m.group(2) else []
                stress_options.append( (stressed_word, grammar_specs) )
            else:
                if word == rso:
                    break
                else:
                    raise Exception()

        _word_stress_option_cache[word] = stress_options

    return _word_stress_option_cache[word]

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

'''for bi, annotated in enumerate(block.get_annotated()):
    elif isinstance(annotated, AnnotatedWord):
        word = annotated.get_word()
        wt = word.get_word()
        annotated_type = annotated.get_type()
        annotated_type_set = set(annotated_type.split(','))https://venturebeat.com/2019/12/03/google-details-ai-that-classifies-chest-x-rays-with-human-level-accuracy/amp/?fbclid=IwAR0-uKZT9s7xMpOitPFe3poXev-CV_jOQH6Gn0J4Yu1glk8Pgx1zdNU_RTw
        stressed_words = {}
        for stress in word.get_stress_options():
            stress_type = stress.get_type()
            stress_type_set = set(stress_type.split(','))
            stressed_words[stress.get_word()] = len(annotated_type_set.intersection(stress_type_set))
        
        if len(set(stressed_words.keys())) == 0:
            stressed_block += wt
        elif len(set(stressed_words.keys())) == 1:
            stressed_block += list(stressed_words.keys())[0]
        else:
            sorted_stressed_words = sorted(stressed_words.items(), key=lambda kv: kv[1], reverse=True)
            stressed_block += sorted_stressed_words[0][0]
        print (stressed_block)
    else:
        raise Exception()'''




exceptions = [
    {
        'article_url': 'http://pakeliui.popo.lt/2019/01/23/apie-tikejima-ir-pasitikejima/',
        'block_index': [4, 5, 7],
        'sub': (u'Doubeyazt', u'Doğubeyazıt')
    }, 
    {
        'article_url': 'http://pakeliui.popo.lt/2019/01/23/apie-tikejima-ir-pasitikejima/',
        'block_index': [4, 5, 7],
        'sub': (u'Doubeyazt', u'Doğubeyazıt')
    }, 
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/istorija_ir_archeologija/S-77994/straipsnis/Radinys-naciu-stovykloje-irodo-tai-ka-politikai-bande-paneigti',
        #'block_index': [2, 3, 8],
        'sub': (u'Vaeka', u'Vařeka')
    },
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/istorija_ir_archeologija/S-77994/straipsnis/Radinys-naciu-stovykloje-irodo-tai-ka-politikai-bande-paneigti',
        #'block_index': [2, 3, 8],
        'sub': (u'Vaekos', u'Vařekos')
    },
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/idomusis_mokslas/S-77663/straipsnis/Skaiciavimo-masinu-istorija-kur-yra-pati-silpniausia-daugumos-siuolaikiniu-procesoriu-vieta-kaip-atsirado-ir-kas-negerai-su-voniNeumanno-architektura-ir-ka-tokio-ekspertai-surado-Intel-procesoriuose-',
        #'block_index': [2, 3, 8],
        'sub': (u'Erds', u'Erdős')
    }
]

if __name__ == "__main__":
    '''strings = [
        'Kiti ekspertai sako, kad pasikeitę prekybos keliai ir vidiniai nesutarimai galėjo privesti milžinišką ir galingą civilizaciją prie išnykimo.',
        'Dėl to galėjo būti kalti patys majai.',
        'A. Hitleriui buvo paskirti sargybiniai ir uždėta neperšaunama liemenė.',
        'Į žvalgybą buvo išsiųsti lėktuvai.',
        'Šį akmenį A. Hitleris iš karto įsakė pašalinti.',
        'Žinoma, pirmiausia turime apibrėžti kas, šiuo atveju, yra frontas.',
        'Šį akmenį A. Hitleris iš karto įsakė pašalinti.',
        'Šioje vietoje trūksta namo.',
        'Einam namo. Nerandu namo.',
        'laba\n–--–-diena',
        'Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.',
        'namo',
        'shit fantastish dog',
        'Tuo metu kai čia lankėsi A. Hitleris nebuvo jokios realios kovos - tačiau ji labai greitai galėjo įsižiebti.',
        'Antrajame pasauliniame kare kartu su savo kariais nesitraukė iš Stalingrado mūšio lauko',
    ]

    for s in strings:
        print ( s )
        replacements, augmented_elements = fused_stress_text(s)
        fused_text = rebuild_text(augmented_elements, replacements)
        print ( fused_text )
        print ( stress_text(s) )
        print (  )'''

    conn = sqlite3.connect('data3.sqlite.db')
    cursor = conn.cursor()

    for i, exception in enumerate(exceptions):
        cursor.execute('SELECT id FROM articles WHERE `url` = ?', (exception['article_url'],))
        for res in cursor:
            if 'article_id' not in exceptions[i]:
                exceptions[i]['article_id'] = []
            exceptions[i]['article_id'].append(res[0])

    cursor.execute('SELECT article_id, `index`, block, url FROM article_blocks JOIN articles ON article_id = id WHERE article_id > 178')

    for article_id, index, block, url in cursor:
        if not block:
            continue

        exc_ = [e for e in exceptions if article_id in e['article_id']]
        fused_replacements, augmented_elements = fused_stress_replacents(block, exc_)
        fused_stressed_text = rebuild_text(augmented_elements, fused_replacements)
        stressed_text = stress_text(block)
        localizations = localize_stressed_text(stressed_text, augmented_elements)

        comparison_replacements, has_inequalities = compare_replacements([fused_replacements, localizations])

        print (article_id, index)
        if has_inequalities:
            rebuilt_text = rebuild_text(augmented_elements, comparison_replacements)
            
            print ()
            print (block)
            print ()
            print (rebuilt_text)
                
        print ('\n=====================')

    conn.close()
from morphological_analyzer import analyze_text
from soap_stressor import stress_text
import re
import sqlite3

_word_stress_option_cache = {}
_stress_re = re.compile(r'\d+. ([^\( )]+) \(([^\)]+)\)')

def get_word_stress_options(word):
    if word not in _word_stress_option_cache:
        raw_stress_options = filter(None, stress_text(word).split('\n'))
        stress_options = []
        for ro in raw_stress_options:
            m = _stress_re.match(ro)
            if m:
                stressed_word = m.group(1)
                grammar_specs = m.group(2).split(' ')
                stress_options.append( (stressed_word, grammar_specs) )
            else:
                if word == ro:
                    break
                else:
                    raise Exception()

        _word_stress_option_cache[word] = stress_options

    return _word_stress_option_cache[word]

def _stress_selector(grammar_type, stress_options):
    for so in stress_options:
        return so

def fused_stress_text(text, exceptions=None, stress_selector=_stress_selector):
    _, augmented_elements = analyze_text(text, exceptions=exceptions)
    stressed_text = u''

    for element in augmented_elements:
        if 'word' in element:
            word = element['word']
            stress_options = get_word_stress_options(word)

            selected_stress = stress_selector(element['type'], stress_options)
            if selected_stress:
                stressed_text += selected_stress[0]
            else:
                stressed_text += word            
        elif 'number' in element:
            stressed_text += str(element['number'])
        elif 'other' in element:
            stressed_text += str(element['other'])
        else:
            raise NotImplementedError()
    
    return stressed_text

'''for bi, annotated in enumerate(block.get_annotated()):
    elif isinstance(annotated, AnnotatedWord):
        word = annotated.get_word()
        wt = word.get_word()
        annotated_type = annotated.get_type()
        annotated_type_set = set(annotated_type.split(','))
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
    print (fused_stress_text('laba\n–--–-diena'))
    print (fused_stress_text('Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.'))
    print (fused_stress_text('namo'))
    print (fused_stress_text('Šioje vietoje trūksta namo!'))
    print (fused_stress_text('Einam namo. Nerandu namo.'))
    print (fused_stress_text('shit fantastish dog'))

    conn = sqlite3.connect('data3.sqlite.db')
    cursor = conn.cursor()

    for i, exception in enumerate(exceptions):
        cursor.execute('SELECT id FROM articles WHERE `url` = ?', (exception['article_url'],))
        for res in cursor:
            if 'article_id' not in exceptions[i]:
                exceptions[i]['article_id'] = []
            exceptions[i]['article_id'].append(res[0])

    cursor.execute('SELECT article_id, `index`, block, url FROM article_blocks JOIN articles ON article_id = id WHERE article_id > 15477')

    for article_id, index, block, url in cursor:
        print (article_id, index)
        exc_ = [e for e in exceptions if article_id in e['article_id']]
        fused_stress_text(block, exc_)

    conn.close()
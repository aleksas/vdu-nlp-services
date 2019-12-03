#!/usr/bin/env python
# -*- coding: utf-8 -*-

from requests import post
from re import compile, sub, search, finditer, findall
import string 
import sqlite3

re_tag = compile(r'<([^<>]+)/>')
re_param = compile(r'([^ =]+)(="([^"]+)")?')

def process_response(response_content, exceptions):
    result = response_content.decode("utf-8")

    elements = []

    for i, tag in enumerate(re_tag.finditer(result)):
        element = {}
        for param in re_param.finditer(tag.group(1)):
            element[param.group(1)] = param.group(3)
        
        if 'space' in element:
            element = {'sep': ' '}
        if 'sep' in element:
            if element['sep'] == '&10;':
                element['sep'] = '\n'
        if 'word' in element:
            for e in exceptions:
                if 'sub' in e:
                    if element['word'] == e['sub'][0]:
                        element['word'] = e['sub'][1]
                
        elements.append(element)
    
    return elements

def augment(text, elements):
    offset = 0
    auagmented_elements = []
    for i, e in enumerate(elements):
        for key in ['word', 'number']:
            if key in e:
                splits = e[key].split(' ')
                for s in splits:
                    m = search(s, text[offset:])
                    if m:
                        span = (offset + m.span()[0], offset + m.span()[1])
                        e_ = dict(e)
                        e_[key] = s
                        e_['span'] = span
                        auagmented_elements.append(e_)
                        
                        offset += m.end(0)
                    else:
                        raise Exception()
    last_index = 0
    inserts = []
    for i, e in enumerate(auagmented_elements):
        if e['span'][0] > last_index:
            inserts.append((last_index, e['span'][0], i))
        last_index = e['span'][1]
    
    if last_index < len(text):
        inserts.append(( last_index , len(text), len(auagmented_elements)))

    for s, e, i in reversed(inserts):
        v = {'span': (s, e), 'other': text[s:e]}
        auagmented_elements.insert(i, v)
        
    return auagmented_elements

def validate(text, elements, augmented_elements):
    recovered_text = ''
    for e in augmented_elements:
        for key in ['word', 'number', 'other']:
            if key in e:
                recovered_text += e[key]
                
    if recovered_text != text:
        raise Exception()

    offset = 0
    forward_spans = []
    for e in elements:
        for key in ['word', 'number']:
            if key in e:
                for s in e[key].split(' '):
                    m = search(s, text[offset:])
                    if m:
                        forward_spans.append((offset + m.span()[0], offset + m.span()[1], s))
                        offset += m.end(0)
                    else:
                        raise Exception()

    offset = len(text)
    backward_spans = []
    for e in reversed(elements):
        for key in ['word', 'number']:
            if key in e:
                for s in reversed(e[key].split(' ')):
                    matches = [it for it in finditer(s,text[:offset])]
                    if matches:
                        m = matches[-1]
                        offset = m.start(0)
                        backward_spans.append((m.span()[0], m.span()[1], s))
                    else:
                        raise Exception()
    
    if forward_spans != list(reversed(backward_spans)):
        raise Exception()

def analyze_text(text, exceptions):
    altered_text = sub(u'[„“]', '"', text)
    altered_text = sub(u'–', '-', altered_text)
    altered_text = sub(u'[^\.,?\'"\[\]\(\)!\-\+=0-9:;a-zA-Zą-žĄ-Ž]+', ' ', altered_text)
    altered_text = sub(u'(([a-zA-Zą-žĄ-Ž]+)([0-9]+))|(([0-9]+)([a-zA-Zą-žĄ-Ž]+))', r' \2 \3 \5 \6 ', altered_text)
    
    data = {
        'tekstas': altered_text,
        'tipas': 'anotuoti',
        'pateikti': 'LM',
        'veiksmas': 'Analizuoti'
    }

    response = post("http://donelaitis.vdu.lt/NLP/nlp.php", data)

    if response.status_code != 200:
        raise Exception(response.reason)

    elements = process_response(response.content, exceptions)

    augmented_elements = augment(text, elements)
    validate(text, elements, augmented_elements)
    return elements

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
    #print (analyze_text('laba\n–--–-diena'))
    #print (analyze_text('Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.'))
    #print (analyze_text('namo'))
    #print (analyze_text('Šioje vietoje trūksta namo!'))
    #print (analyze_text('Einam namo. Nerandu namo.'))

    conn = sqlite3.connect('data3.sqlite.db')
    cursor = conn.cursor()

    for i, exception in enumerate(exceptions):
        cursor.execute('SELECT id FROM articles WHERE `url` = ?', (exception['article_url'],))
        for res in cursor:
            if 'article_id' not in exceptions[i]:
                exceptions[i]['article_id'] = []
            exceptions[i]['article_id'].append(res[0])

    cursor.execute('SELECT article_id, `index`, block, url FROM article_blocks JOIN articles ON article_id = id WHERE article_id > 19420')

    for article_id, index, block, url in cursor:
        print (article_id, index)
        exc_ = [e for e in exceptions if article_id in e['article_id']]
        analyze_text(block, exc_)

    conn.close()
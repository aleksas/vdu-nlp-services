#!/usr/bin/env python
# -*- coding: utf-8 -*-

from requests import post
from re import compile, sub
import string 
import sqlite3

re_tag = compile(r'<([^<>]+)/>')
re_param = compile(r'([^ =]+)(="([^"]+)")?')

def alter_text(text):
    spec_set = set(list(u'-\n –'))

    try:
        chars = (''.join(set(text) - spec_set)).replace(']', r'\]').replace('[', r'\[')
        spec_chars_only = sub(u'[' + chars  + ']', '', text) if chars else ''
    except TypeError as e:
        print(e)
    altered_text = text.replace(u'–', '-').replace(u'\n', ' ')
    return altered_text, spec_chars_only

def process_response(response_content, spec_chars_only):
    result = response_content.decode("utf-8")

    elements = []
    offset = 0

    for i, tag in enumerate(re_tag.finditer(result)):
        element = {}
        for param in re_param.finditer(tag.group(1)):
            element[param.group(1)] = param.group(3)
        
        if 'space' in element:
            if spec_chars_only[i - offset] == '\n':
                element = {'sep': '\n'}
        elif 'sep' in element and element['sep'] == '-':
            if spec_chars_only[i - offset] == u'–':
                element['sep'] = u'–'
        else:
            offset += 1 - (element['word'].count(' ') if 'word' in element else 0)

        elements.append(element)
    
    return elements

def validate(text, elements):
    reconstructed = ''
    for e in elements:
        if 'word' in e:
            reconstructed += e['word']
        elif 'space' in e:
            reconstructed += ' '
        elif 'sep' in e:
            if e['sep'] == None:
                pass
            else:
                reconstructed += e['sep']
        elif 'number' in e:
            reconstructed += e['number']
        else:
            NotImplemented

def analyze_text(text):
    altered_text, spec_chars_only = alter_text(text)
    
    data = {
        'tekstas': altered_text,
        'tipas': 'anotuoti',
        'pateikti': 'LM',
        'veiksmas': 'Analizuoti'
    }

    response = post("http://donelaitis.vdu.lt/NLP/nlp.php", data)

    if response.status_code != 200:
        raise Exception(response.reason)

    elements = process_response(response.content, spec_chars_only)

    validate(text, elements)
    
    return elements

if __name__ == "__main__":
    #print (analyze_text('laba\n–--–-diena'))
    #print (analyze_text('Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.'))
    #print (analyze_text('namo'))
    #print (analyze_text('Šioje vietoje trūksta namo!'))
    #print (analyze_text('Einam namo. Nerandu namo.'))

    conn = sqlite3.connect('data3.sqlite.db')
    cursor = conn.cursor()

    cursor.execute('SELECT article_id, `index`, block FROM article_blocks WHERE article_id > 1082')

    for article_id, index, block in cursor:
        print (article_id, index)
        analyze_text(block)

    conn.close()
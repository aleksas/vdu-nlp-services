#!/usr/bin/env python
# -*- coding: utf-8 -*-

from requests import post
from re import compile, sub
import string 

re_tag = compile(r'<([^<>]+)/>')
re_param = compile(r'([^ =]+)(="([^"]+)")?')

def alter_text(text):
    spec_set = set(u'-\n –')
    spec_chars_only = sub(u'[' + ''.join(set(text) - spec_set) + ']', '', text)
    altered_text = text.replace(u'–', '-').replace(u'\n', ' ')
    return altered_text, spec_chars_only

def process_response(response_content):
    result = response_content.decode("utf-8")

    elements = []
    offset = 0

    for i, tag in enumerate(re_tag.finditer(result)):
        element = {}
        for param in re_param.finditer(tag.group(1)):
            element[param.group(1)] = param.group(3)
        
        if 'space' in element:
            if spec_chars_only[i - offset] == '\n':
                element = {'sep': '&10;'}
        elif 'sep' in element and element['sep'] == '-':
            if spec_chars_only[i - offset] == u'–':
                element['sep'] = u'–'
        else:
            offset += 1 - (element['word'].count(' ') if 'word' in element else 0)

        elements.append(element)
    
    return elements

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

    return process_response(response.content)

if __name__ == "__main__":
    print (analyze_text('laba\n–--–-diena'))
    print (analyze_text('Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.'))
    print (analyze_text('namo'))
    print (analyze_text('Šioje vietoje trūksta namo!'))
    print (analyze_text('Einam namo. Nerandu namo.'))

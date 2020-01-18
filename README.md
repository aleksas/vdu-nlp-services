[![Build Status](https://travis-ci.org/aleksas/vdu-nlp-services.svg?branch=master)](https://travis-ci.org/aleksas/vdu-nlp-services)
[![PyPi version](https://pypip.in/v/vdu-nlp-services/badge.png)](https://pypi.org/project/vdu-nlp-services/)

# vdu-nlp-services

## Function Reference

### Reference

#### analyze_text

Perform morphological analysis

```python
from vdu_nlp_services import analyze_text

res = analyze_text(u'Laba diena!', include_lemmas=True)
print (res)
```
```sh
([{u'lemma': u'laba diena', u'word': u'Laba diena', u'type': u'jst.'}, {u'sep': u'!'}, {u'p': None}], [{u'lemma': u'laba diena', 'span': (0, 4), u'word': u'Laba', u'type': u'jst.'}, {'other': u' ', 'span': (4, 5)}, {u'lemma': u'laba diena', 'span': (5, 10), u'word': u'diena', u'type': u'jst.'}, {'other': u'!', 'span': (10, 11)}])
```
#### stress_text

Accentuate text

```python
from vdu_nlp_services import stress_text

res = stress_text(u'Laba diena!')
print (res)
```
```sh
'Laba` diena`!'
```

## Install

### PyPi
```bash
pip install vdu-nlp-services
```
### Git
```bash
pip install git+https://github.com/aleksas/vdu-nlp-services.git
```

[![Build Status](https://travis-ci.org/aleksas/vdu-nlp-services.svg?branch=master)](https://travis-ci.org/aleksas/vdu-nlp-services)

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
[{'word': 'Laba diena', 'lemma': 'laba diena', 'type': 'jst.'}, {'sep': '!'}, {'p': None}]
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

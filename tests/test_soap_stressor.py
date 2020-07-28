#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from vdu_nlp_services import analyze_text, stress_text, stress_word

class SimpleTestCase(TestCase):
    def test_1(self):
        stress_text(u'Laba diena draugai! Kaip jums sekasi? Vienas, du, trys.')
        stress_text(u'namo')
        stress_text(u'Šioje vietoje trūksta namo!')
        stress_text(u'Einam namo!')

    def test_2(self):
        stress_word(u'Laba')
        stress_word(u'keliai')

    def test_3(self):
        res = [(x[0], list(x[1])) for x in stress_word(u'toj')]
        expected = [(u'to~j', [u'įvrd.', u'mot.gim.', u'vnsk.', u'Vt.', u'neįvardž.', u'sutrmp.'])]
        self.assertEqual(res, expected)

if __name__ == '__main__':
    main()
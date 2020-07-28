#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from vdu_nlp_services import analyze_text, stress_text

class SimpleTestCase(TestCase):
    def test_1(self):
        stress_text('Laba diena draugai! Kaip jums sekasi? Vienas, du, trys.')
        stress_text('namo')
        stress_text('Šioje vietoje trūksta namo!')
        stress_text('Einam namo!')

    def test_2(self):
        stress_word('Laba')
        stress_word('keliai')

    def test_3(self):
        res = [(x[0], list(x[1])) for x in stress_word('toj')]
        res == ['to~j', ['įvrd.', 'mot.gim.', 'vnsk.', 'Vt.', 'neįvardž.', 'sutrmp.']]

        self.assertEqual(res, ['to~j', ['įvrd.', 'mot.gim.', 'vnsk.', 'Vt.', 'neįvardž.', 'sutrmp.']])

if __name__ == '__main__':
    main()
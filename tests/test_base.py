#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from vdu_nlp_services import analyze_text, stress_text

class SimpleTestCase(TestCase):
    def test_1(self):
        text = 'labas'
        analyze_text(text)

    def test_2(self):
        analyze_text(u'laba\n–--–-diena')

    def test_3(self):
        analyze_text(u'Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.')

    def test_4(self):
        analyze_text(u'namo')

    def test_5(self):
        analyze_text(u'Šioje vietoje trūksta namo!')

    def test_6(self):
        analyze_text(u'Einam namo. Nerandu namo.')

    def test_7(self):
        exceptions = [
            {
                'sub': (u'Doubeyazt', u'Doğubeyazıt')
            }, 
            {
                'sub': (u'Doubeyazt', u'Doğubeyazıt')
            }, 
            {
                'sub': (u'Vaeka', u'Vařeka')
            },
            {
                'sub': (u'Vaekos', u'Vařekos')
            },
            {
                'sub': (u'Erds', u'Erdős')
            }
        ]

        analyze_text(u'a Doğubeyazıt b Doğubeyazıt c Vařeka d Erdős e', exceptions=exceptions)

if __name__ == '__main__':
    main()
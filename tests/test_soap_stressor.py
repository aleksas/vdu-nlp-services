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

if __name__ == '__main__':
    main()
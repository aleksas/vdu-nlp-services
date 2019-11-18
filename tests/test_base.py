from sys import path
path.append('..')

from unittest import TestCase, main
from vdu_nlp_services import analyze_text, stress_text

class SimpleTestCase(TestCase):
    def test_1(self):
        text = 'labas'
        analyze_text(text)

    def test_2(self):
        text = 'labas'
        stress_text(text)

if __name__ == '__main__':
    main()
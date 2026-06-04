import unittest
import random
from dfa import DFA
from grader import Grader
from gradescope_utils.autograder_utils.decorators import weight, visibility

class TestHW1(unittest.TestCase):
    def setUp(self):
        self.grader = Grader()

    @weight(10)
    @visibility("visible")
    def test_problem1(self):
        """Problem 1: Binary number divisible by 3"""
        dfa = DFA(set(), set(), {}, "", set())
        dfa.from_json("sol1.json")

        def divisibility_test(i):
            if i < 20:
                n = i
            else:
                n = random.randint(0, 10000)
            return (bin(n)[2:], n % 3 == 0)

        result, message = self.run_grader_test(dfa, divisibility_test, 100)
        self.assertTrue(result, message)

    @weight(5)
    @visibility("visible")
    def test_problem2a(self):
        """Problem 2a: Even number of 'a's"""
        dfa = DFA(set(), set(), {}, "", set())
        dfa.from_json("sol2a.json")

        def even_a_test(_):
            length = random.randint(0, 20)
            s = "".join(random.choice("ab") for _ in range(length))
            return (s, s.count('a') % 2 == 0)

        result, message = self.run_grader_test(dfa, even_a_test, 50)
        self.assertTrue(result, message)

    @weight(5)
    @visibility("visible")
    def test_problem2b(self):
        """Problem 2b: At least one 'b'"""
        dfa = DFA(set(), set(), {}, "", set())
        dfa.from_json("sol2b.json")

        def at_least_one_b_test(_):
            length = random.randint(0, 20)
            s = "".join(random.choice("ab") for _ in range(length))
            return (s, 'b' in s)

        result, message = self.run_grader_test(dfa, at_least_one_b_test, 50)
        self.assertTrue(result, message)

    def run_grader_test(self, automaton, test_func, iterations):
        for i in range(iterations):
            input_string, expected = test_func(i)
            result = automaton.accepts(input_string)
            if expected != result:
                return False, f"Failed for input '{input_string}': expected {expected}, got {result}"
        return True, ""

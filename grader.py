from typing import Callable, Protocol
import random


class Grader:
    def __init__(self) -> None:
        self.tests = []

    def add_test(self, test: Callable, iterations: int = 10) -> None:
        self.tests.append((test, iterations))

    def run(self, automaton) -> None:
        for test_num, (test, iterations) in enumerate(self.tests):
            result = self.run_test(automaton, test, iterations)
            if result:
                print(f"\033[92mTest {test_num + 1}: Passed\033[0m")
            else:
                print(f"\033[91mTest {test_num + 1}: Failed\033[0m")

    def run_test(self, automaton, test: Callable, iterations: int) -> bool:
        for i in range(iterations):
            input_string, expected = test(i)
            result = automaton.accepts(input_string)
            if expected != result:
                return False
        return True


def main():
    print("DFA Tests")
    from dfa import DFA

    dfa = DFA(
        states={"q0", "q1", "q2"},
        alphabet={"1", "0"},
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q2", "1": "q0"},
            "q2": {"0": "q1", "1": "q2"},
        },
        start_state="q0",
        accept_states={"q0"},
    )

    wrong_dfa = DFA(
        states={"q0", "q1", "q2"},
        alphabet={"1", "0"},
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q2", "1": "q0"},
            "q2": {"0": "q1", "1": "q3"},
        },
        start_state="q0",
        accept_states={"q0", "q2"},
    )

    dfa_autograder = Grader()
    dfa_autograder.add_test(lambda x: (bin(x * 3)[2:], True), 10)
    dfa_autograder.add_test(lambda x: (bin(x * 3 + 1)[2:], False), 10)
    dfa_autograder.add_test(lambda x: (bin(x)[2:], x % 3 == 0), 10)

    def random_test_dfa(_: int):
        n = random.randint(0, 1000)
        return (bin(n)[2:], n % 3 == 0)

    dfa_autograder.add_test(random_test_dfa, 2)

    print("Testing correct DFA:")
    dfa_autograder.run(dfa)

    print("\nTesting incorrect DFA:")
    dfa_autograder.run(wrong_dfa)

    print("\nNFA Tests")
    from nfa import NFA

    nfa_contains_ab = NFA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        transitions={
            "q0": {"a": ["q0", "q1"], "b": ["q0"]},
            "q1": {"b": ["q2"]},
            "q2": {"a": ["q2"], "b": ["q2"]},
        },
        start_state="q0",
        accept_states={"q2"},
    )
    nfa_autograder = Grader()
    nfa_autograder.add_test(lambda i: ("a" * i + "ab", True))
    nfa_autograder.add_test(lambda i: ("b" * i + "a", False))

    print("Testing NFA for strings containing 'ab':")
    nfa_autograder.run(nfa_contains_ab)

    print("\nPDA Tests")
    from pda import PDA

    pda_an_bn = PDA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        stack_alphabet={"A", "Z"},
        transitions={
            "q0": {"a": [("q0", "A", "")], "": [("q1", "", "")]},
            "q1": {"b": [("q1", "", "A")], "": [("q2", "", "Z")]},
        },
        start_state="q0",
        accept_states={"q2"},
    )
    pda_autograder = Grader()
    pda_autograder.add_test(lambda i: ("a" * i + "b" * i, True))
    pda_autograder.add_test(lambda i: ("a" * (i + 1) + "b" * i, False))

    print("Testing PDA for a^n b^n:")
    pda_autograder.run(pda_an_bn)


if __name__ == "__main__":
    main()

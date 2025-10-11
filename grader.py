from typing import Callable
from dfa import DFA
import random


class Grader:
    def __init__(self) -> None:
        self.tests = []

    def add_test(self, test: Callable, iterations: int = 10) -> None:
        self.tests.append((test, iterations))

    def run(self, dfa: DFA) -> None:
        for test_num, (test, iterations) in enumerate(self.tests):
            result = self.run_test(dfa, test, iterations)
            if result:
                print(f"\033[92mTest {test_num + 1}: Passed\033[0m")
            else:
                print(f"\033[91mTest {test_num + 1}: Failed\033[0m")

    def run_test(self, dfa: DFA, test: Callable, iterations: int) -> bool:
        for i in range(iterations):
            input_string, expected = test(i)
            result = dfa.accepts(input_string)
            if expected != result:
                return False
        return True


def main():
    # Constructing a DFA that accepts binary strings that are multiples of 3
    dfa = DFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'1', '0'},
        transitions={
            'q0': {'0': 'q0', '1': 'q1'},
            'q1': {'0': 'q2', '1': 'q0'},
            'q2': {'0': 'q1', '1': 'q2'}
        },
        start_state='q0',
        accept_states={'q0'}
    )

    wrong_dfa = DFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'1', '0'},
        transitions={
            'q0': {'0': 'q0', '1': 'q1'},
            'q1': {'0': 'q2', '1': 'q0'},
            'q2': {'0': 'q1', '1': 'q3'}
        },
        start_state='q0',
        accept_states={'q0', 'q2'}
    )

    autograder = Grader()

    autograder.add_test(
            lambda x: (bin(x * 3)[2:], True), 10
    )
    autograder.add_test(
            lambda x: (bin(x * 3 + 1)[2:], False), 10
    )

    autograder.add_test(
            lambda x: (bin(x)[2:], x % 3 == 0), 10
    )

    def random_test(_: int):
        n = random.randint(0, 1000)
        return (bin(n)[2:], n % 3 == 0)
    autograder.add_test(
            random_test, 2
    )

    print("Testing correct DFA:")
    autograder.run(dfa)

    print("\nTesting incorrect DFA:")
    autograder.run(wrong_dfa)


if __name__ == "__main__":
    main()

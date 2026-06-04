from collections import deque
import json
from pathlib import Path


class PDA:
    def __init__(
        self, states, alphabet, stack_alphabet, transitions, start_state, accept_states
    ):
        self.states = states
        self.alphabet = alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def accepts(self, input_string):
        if "$" not in self.stack_alphabet:
            self.stack_alphabet.add("$")

        q = deque([(self.start_state, tuple(input_string), ("$",))])
        visited = set([(self.start_state, tuple(input_string), ("$",))])

        while q:
            current_state, remaining_input, stack = q.popleft()

            if not remaining_input and current_state in self.accept_states:
                return True

            for symbol in ["", "\\epsilon"]:
                if (
                    current_state in self.transitions
                    and symbol in self.transitions[current_state]
                ):
                    for next_state, push, pop in self.transitions[current_state][
                        symbol
                    ]:
                        if stack:
                            stack_top = stack[-1] if stack else None
                            if pop in ["", "\\epsilon"] or pop == stack_top:
                                new_stack = list(stack)
                                if pop not in ["", "\\epsilon"]:
                                    new_stack.pop()

                                if push not in ["", "\\epsilon"]:
                                    for push_symbol in reversed(push):
                                        new_stack.append(push_symbol)

                                new_config = (
                                    next_state,
                                    remaining_input,
                                    tuple(new_stack),
                                )
                                if new_config not in visited:
                                    q.append(new_config)
                                    visited.add(new_config)

            if remaining_input:
                symbol = remaining_input[0]
                rest_of_input = remaining_input[1:]
                if (
                    current_state in self.transitions
                    and symbol in self.transitions[current_state]
                ):
                    for next_state, push, pop in self.transitions[current_state][
                        symbol
                    ]:
                        if stack:
                            stack_top = stack[-1] if stack else None
                            if pop in ["", "\\epsilon"] or pop == stack_top:
                                new_stack = list(stack)
                                if pop not in ["", "\\epsilon"]:
                                    new_stack.pop()

                                if push not in ["", "\\epsilon"]:
                                    for push_symbol in reversed(push):
                                        new_stack.append(push_symbol)

                                new_config = (
                                    next_state,
                                    rest_of_input,
                                    tuple(new_stack),
                                )
                                if new_config not in visited:
                                    q.append(new_config)
                                    visited.add(new_config)
        return False

    def to_json(self, path="pda.json"):
        nodes = [
            {
                "name": s,
                "group": (
                    "start-accept"
                    if s == self.start_state and s in self.accept_states
                    else "start"
                    if s == self.start_state
                    else "accept"
                    if s in self.accept_states
                    else "normal"
                ),
            }
            for s in self.states
        ]

        links = []
        for src, transitions in self.transitions.items():
            for symbol, dsts in transitions.items():
                for dst in dsts:
                    links.append(
                        {
                            "source": src,
                            "target": dst[0],
                            "label": f"{symbol or '\\epsilon'},{dst[2] or '\\epsilon'} -> {dst[1] or '\\epsilon'}",
                        }
                    )

        data = {"nodes": nodes, "links": links}

        Path(path).write_text(json.dumps(data, indent=2))
        print(f"Exported PDA to {path}")
        return data

    def from_json(self, path="pda.json"):
        with open(path, "r") as f:
            data = json.load(f)

        states = [node["name"] for node in data["nodes"]]

        start_state = None
        accept_states = set()
        for node in data["nodes"]:
            group = node.get("group")
            if group and "start" in group:
                start_state = node["name"]
            if group and "accept" in group:
                accept_states.add(node["name"])
        if start_state is None:
            raise ValueError("No start state defined in JSON")

        transitions = {state: {} for state in states}
        alphabet = set()
        stack_alphabet = set()

        for link in data["links"]:
            src = link["source"]
            dst = link["target"]
            full_label = link.get("label", "")
            for label in full_label.split("\n"):
                label = label.strip()
                if not label:
                    continue

                if "->" in label:
                    parts = label.split("->")
                    push = parts[1].strip()
                    left = parts[0].strip()
                elif ";" in label:
                    parts = label.split(";")
                    push = parts[1].strip()
                    left = parts[0].strip()
                else:
                    push = ""
                    left = label

                if "," in left:
                    l_parts = [p.strip() for p in left.split(",")]
                    pop = l_parts[-1]
                    symbols = l_parts[:-1]
                    if not symbols:
                        symbols = [""]
                else:
                    symbols = [left]
                    pop = ""

                for symbol in symbols:
                    if symbol in ["", "\\epsilon"]:
                        symbol = ""
                    if pop in ["", "\\epsilon"]:
                        pop = ""
                    if push in ["", "\\epsilon"]:
                        push = ""

                    if symbol:
                        alphabet.add(symbol)
                    if pop:
                        stack_alphabet.add(pop)
                    if push:
                        for char in push:
                            stack_alphabet.add(char)

                    if src not in transitions:
                        transitions[src] = {}
                    if symbol not in transitions[src]:
                        transitions[src][symbol] = []
                    transitions[src][symbol].append((dst, push, pop))

        self.states = states
        self.alphabet = alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states


def main():
    print("Testing PDA for a^n b^n, n>=0")
    pda_an_bn = PDA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        stack_alphabet={"A", "$"},
        transitions={
            "q0": {"a": [("q0", "A", "")], "": [("q1", "", "")]},
            "q1": {"b": [("q1", "", "A")], "": [("q2", "", "$")]},
        },
        start_state="q0",
        accept_states={"q2"},
    )
    test_strings_an_bn = {
        "": True,
        "ab": True,
        "aabb": True,
        "aaabbb": True,
        "a": False,
        "b": False,
        "aab": False,
        "abb": False,
    }
    for s, expected in test_strings_an_bn.items():
        assert pda_an_bn.accepts(s) == expected
        print(f"'{s}': {pda_an_bn.accepts(s)}")

    print("\nTesting PDA to/from JSON")
    pda_an_bn.to_json("pda_an_bn.json")
    pda_loaded = PDA(set(), set(), set(), {}, "", set())
    pda_loaded.from_json("pda_an_bn.json")
    for s, expected in test_strings_an_bn.items():
        assert pda_loaded.accepts(s) == expected
    print("JSON serialization and deserialization successful.")

    print("\nTesting PDA for w c w^R")
    pda_wcwr = PDA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b", "c"},
        stack_alphabet={"A", "B", "$"},
        transitions={
            "q0": {
                "a": [("q0", "A", "")],
                "b": [("q0", "B", "")],
                "c": [("q1", "", "")],
            },
            "q1": {
                "a": [("q1", "", "A")],
                "b": [("q1", "", "B")],
                "": [("q2", "", "$")],
            },
        },
        start_state="q0",
        accept_states={"q2"},
    )
    test_strings_wcwr = {
        "c": True,
        "aca": True,
        "bcb": True,
        "abcba": True,
        "abccba": False,
        "a": False,
        "b": False,
        "acb": False,
        "abc": False,
    }
    for s, expected in test_strings_wcwr.items():
        assert pda_wcwr.accepts(s) == expected
        print(f"'{s}': {pda_wcwr.accepts(s)}")


if __name__ == "__main__":
    main()

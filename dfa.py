import json
from pathlib import Path


class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def accepts(self, input_string):
        current_state = self.start_state
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            if (
                current_state not in self.transitions
                or symbol not in self.transitions[current_state]
            ):
                return False
            current_state = self.transitions[current_state][symbol]
        return current_state in self.accept_states

    def to_json(self, path="dfa.json"):
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
            for symbol, dst in transitions.items():
                links.append({"source": src, "target": dst, "label": symbol})

        data = {"nodes": nodes, "links": links}

        Path(path).write_text(json.dumps(data, indent=2))
        print(f"Exported DFA to {path}")
        return data

    def from_json(self, path="dfa.json"):
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

        for link in data["links"]:
            src = link["source"]
            dst = link["target"]
            symbol = link.get("label", "a")
            alphabet.add(symbol)
            if src not in transitions:
                transitions[src] = {}
            transitions[src][symbol] = dst

        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def to_nfa(self):
        from nfa import NFA

        nfa_transitions = {}
        for state, transitions in self.transitions.items():
            nfa_transitions[state] = {}
            for symbol, next_state in transitions.items():
                nfa_transitions[state][symbol] = [next_state]

        return NFA(
            states=self.states,
            alphabet=self.alphabet,
            transitions=nfa_transitions,
            start_state=self.start_state,
            accept_states=self.accept_states,
        )


def main():
    print("Testing DFA for even number of 'a's")
    dfa_even_a = DFA(
        states={"q0", "q1"},
        alphabet={"a", "b"},
        transitions={
            "q0": {"a": "q1", "b": "q0"},
            "q1": {"a": "q0", "b": "q1"},
        },
        start_state="q0",
        accept_states={"q0"},
    )
    test_strings_even_a = {
        "": True,
        "b": True,
        "aa": True,
        "bab": False,
        "bb": True,
        "aaaa": True,
        "aab": True,
        "a": False,
        "ab": False,
        "aaab": False,
    }
    for s, expected in test_strings_even_a.items():
        assert dfa_even_a.accepts(s) == expected
        print(f"'{s}': {dfa_even_a.accepts(s)}")

    print("\nTesting DFA to/from JSON")
    dfa_even_a.to_json("dfa_even_a.json")
    dfa_loaded = DFA(set(), set(), {}, "", set())
    dfa_loaded.from_json("dfa_even_a.json")
    for s, expected in test_strings_even_a.items():
        assert dfa_loaded.accepts(s) == expected
    print("JSON serialization and deserialization successful.")

    print("\nTesting DFA for strings ending in 'ab'")
    dfa_ends_in_ab = DFA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        transitions={
            "q0": {"a": "q1", "b": "q0"},
            "q1": {"a": "q1", "b": "q2"},
            "q2": {"a": "q1", "b": "q0"},
        },
        start_state="q0",
        accept_states={"q2"},
    )
    test_strings_ends_in_ab = {
        "ab": True,
        "aab": True,
        "bab": True,
        "aaab": True,
        "": False,
        "a": False,
        "b": False,
        "ba": False,
        "aba": False,
    }
    for s, expected in test_strings_ends_in_ab.items():
        assert dfa_ends_in_ab.accepts(s) == expected
        print(f"'{s}': {dfa_ends_in_ab.accepts(s)}")

    print("\nTesting DFA to NFA conversion")
    nfa_from_dfa = dfa_ends_in_ab.to_nfa()
    for s, expected in test_strings_ends_in_ab.items():
        assert nfa_from_dfa.accepts(s) == expected
    print("DFA to NFA conversion successful.")


if __name__ == "__main__":
    main()

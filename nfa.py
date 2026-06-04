import json
from pathlib import Path


class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def _epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()

            epsilon_transitions = []
            if state in self.transitions:
                epsilon_transitions.extend(self.transitions[state].get("", []))
                epsilon_transitions.extend(self.transitions[state].get("\\epsilon", []))

            for next_state in epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def accepts(self, input_string):
        current_states = self._epsilon_closure({self.start_state})
        for symbol in input_string:
            if symbol not in self.alphabet and symbol != "":
                return False

            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states.update(self.transitions[state][symbol])

            current_states = self._epsilon_closure(next_states)

        return not current_states.isdisjoint(self.accept_states)

    def to_json(self, path="nfa.json"):
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
                    links.append({"source": src, "target": dst, "label": symbol})

        data = {"nodes": nodes, "links": links}

        Path(path).write_text(json.dumps(data, indent=2))
        print(f"Exported NFA to {path}")
        return data

    def from_json(self, path="nfa.json"):
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
            label = link.get("label", "a")
            for symbol in label.split(","):
                symbol = symbol.strip()
                if symbol == "\\epsilon":
                    symbol = ""
                if symbol != "":
                    alphabet.add(symbol)
                if src not in transitions:
                    transitions[src] = {}
                if symbol not in transitions[src]:
                    transitions[src][symbol] = []
                transitions[src][symbol].append(dst)

        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def to_dfa(self):
        from dfa import DFA

        dfa_transitions = {}
        dfa_start_state = frozenset(self._epsilon_closure({self.start_state}))

        worklist = [dfa_start_state]
        dfa_states_set = {dfa_start_state}

        state_map = {dfa_start_state: "q0"}
        next_state_idx = 1

        while worklist:
            current_nfa_states = worklist.pop(0)
            current_dfa_state_name = state_map[current_nfa_states]
            dfa_transitions[current_dfa_state_name] = {}

            for symbol in self.alphabet:
                next_nfa_states = set()
                for nfa_state in current_nfa_states:
                    if (
                        nfa_state in self.transitions
                        and symbol in self.transitions[nfa_state]
                    ):
                        next_nfa_states.update(self.transitions[nfa_state][symbol])

                if not next_nfa_states:
                    continue

                epsilon_closure_next = frozenset(self._epsilon_closure(next_nfa_states))

                if epsilon_closure_next not in dfa_states_set:
                    dfa_states_set.add(epsilon_closure_next)
                    worklist.append(epsilon_closure_next)
                    state_map[epsilon_closure_next] = f"q{next_state_idx}"
                    next_state_idx += 1

                dfa_transitions[current_dfa_state_name][symbol] = state_map[
                    epsilon_closure_next
                ]

        dfa_accept_states = {
            state_map[s] for s in dfa_states_set if not self.accept_states.isdisjoint(s)
        }

        return DFA(
            states=set(state_map.values()),
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            start_state=state_map[dfa_start_state],
            accept_states=dfa_accept_states,
        )


def main():
    print("Testing NFA for strings containing 'ab'")
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
    test_strings_contains_ab = {
        "ab": True,
        "aab": True,
        "bab": True,
        "aaab": True,
        "baba": True,
        "b": False,
        "a": False,
        "ba": False,
        "": False,
    }
    for s, expected in test_strings_contains_ab.items():
        assert nfa_contains_ab.accepts(s) == expected
        print(f"'{s}': {nfa_contains_ab.accepts(s)}")

    print("\nTesting NFA to/from JSON")
    nfa_contains_ab.to_json("nfa_contains_ab.json")
    nfa_loaded = NFA(set(), set(), {}, "", set())
    nfa_loaded.from_json("nfa_contains_ab.json")
    for s, expected in test_strings_contains_ab.items():
        assert nfa_loaded.accepts(s) == expected
    print("JSON serialization and deserialization successful.")

    print("\nTesting NFA with epsilon transitions")
    nfa_epsilon = NFA(
        states={"q0", "q1", "q2", "q3", "q4"},
        alphabet={"a", "b", "c"},
        transitions={
            "q0": {"a": ["q1"]},
            "q1": {"\\epsilon": ["q2"]},
            "q2": {"b": ["q3"]},
            "q3": {"": ["q4"]},
            "q4": {"c": ["q4"]},
        },
        start_state="q0",
        accept_states={"q3", "q4"},
    )
    test_strings_epsilon = {
        "ab": True,
        "abc": True,
        "abcc": True,
        "a": False,
        "b": False,
        "c": False,
        "": False,
    }
    for s, expected in test_strings_epsilon.items():
        assert nfa_epsilon.accepts(s) == expected
        print(f"'{s}': {nfa_epsilon.accepts(s)}")

    print("\nTesting NFA to DFA conversion")
    dfa_from_nfa = nfa_contains_ab.to_dfa()
    for s, expected in test_strings_contains_ab.items():
        assert dfa_from_nfa.accepts(s) == expected
    print("NFA to DFA conversion successful for 'contains ab'.")

    dfa_from_nfa_epsilon = nfa_epsilon.to_dfa()
    for s, expected in test_strings_epsilon.items():
        assert dfa_from_nfa_epsilon.accepts(s) == expected
    print("NFA to DFA conversion successful for NFA with epsilon transitions.")


if __name__ == "__main__":
    main()

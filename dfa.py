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
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False
            current_state = self.transitions[current_state][symbol]
        return current_state in self.accept_states

    def to_json(self, path="dfa.json"):
        nodes = [
            {
                "name": s,
                "group": (
                    "start" if s == self.start_state else
                    "accept" if s in self.accept_states else
                    "normal"
                ),
            }
            for s in self.states
        ]

        links = []
        for src, transitions in self.transitions.items():
            for symbol, dst in transitions.items():
                links.append({
                    "source": src,
                    "target": dst,
                    "label": symbol
                })

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
            if node.get("group") == "start":
                start_state = node["name"]
            elif node.get("group") == "accept":
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

def main():
    dfa = DFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'a', 'b'},
        transitions={
            'q0': {'a': 'q1'},
            'q1': {'a': 'q1', 'b': 'q2', 'c': 'q1'},
            'q2': {'a': 'q2', 'b': 'q0'}
        },
        start_state='q0',
        accept_states={'q1'}
    )

    dfa.to_json()
    dfa.from_json()

    print(dfa.accepts("aba"))
    print(dfa.accepts("a"))

if __name__ == "__main__":
    main()

class DeterministicFiniteAutomaton(object):
    def __init__(
            self,
            start_state,
            transition_function={},
            accept_states=[]
    ):
        self.start_state = start_state
        self._transition_function = transition_function
        self.accept_states = accept_states
        self.reset()

    def __repr__(self):
        return '({0}{1})'.format(
            self.current_state or 'dead',
            '*' if self.accepting else ''
        )

    @property
    def start_state(self):
        '''The starting state of the automaton'''
        return self._start_state

    @start_state.setter
    def start_state(self, value):
        self._start_state = value

    @property
    def current_state(self):
        '''The current state of the automaton'''
        return self._current_state

    @current_state.setter
    def current_state(self, value):
        self._current_state = value

    @property
    def accept_states(self):
        '''The accepting states of the automaton'''
        return self._accept_states

    @accept_states.setter
    def accept_states(self, value):
        self._accept_states = value

    def transition(self, state, symbol, default=None):
        return self._transition_function.get((state, symbol), default)

    def add_transition(self, state, symbol, t_state):
        self._transition_function[(state, symbol)] = t_state

    def add_multisymbol_transition(self, state, symbols, t_state):
        for symbol in symbols:
            self.add_transition(state, symbol, t_state)

    @property
    def alphabet(self):
        '''The alphabet over which the automaton accepts languages'''
        return reduce(
            lambda  alpha, (q, x): alpha | set([x]) if x else alpha,
            self._transition_function.iterkeys(),
            set()
        )

    @property
    def states(self):
        '''The available states of the automaton'''
        return reduce(
            lambda states, ((q, x), p): states | set([p, q]),
            self._transition_function.iteritems(),
            set()
        )

    @property
    def dead(self):
        '''True if the automaton has read a symbol for which it has no valid
        transition

        '''
        return not self.current_state

    @property
    def accepting(self):
        '''True if the automaton is in an accepting state'''
        return self.current_state in self.accept_states

    def reset(self):
        self.current_state = self.start_state
        return self

    def read(self, symbol):
        self.current_state = self.transition(
            self.current_state,
            symbol
        )
        return self

    def read_seq(self, seq):
        return reduce(
            lambda a, b: a.read(b),
            seq,
            self,
        )

class NondeterministicFiniteAutomaton(DeterministicFiniteAutomaton):

    def __repr__(self):
        return "({{{0}}}{1})".format(
            ','.join(
                [str(x) for x in self.current_state]
            ) or 'dead',
            '*' if self.accepting else ''
        )

    def add_transition(self, state, symbol, t_state):
        self.transition(
            state,
            symbol,
            []
        ).append(t_state)

    def add_transitions(self, state, symbol, t_states):
        self.transition(
            state,
            symbol,
            []
        ).extend(t_states)

    def _transition_set(self, states, symbol):
        delta = self.transition
        return reduce(
            lambda all_states, q_states: all_states | set(q_states),
            [delta(q, symbol, []) for q in states],
            set(),
        )

    @property
    def accepting(self):
        for state in self.current_state:
            if state in self.accept_states:
                return True
        return False

    @property
    def states(self):
        return reduce(
            lambda states, ((q, x), p): states | set(p) | set([q]),
            self._transition_function.iteritems(),
            set(),
        )

    def reset(self):
        self.current_state = set([self.start_state])
        return self

    def read(self, symbol):
        self.current_state = self._transition_set(self.current_state, symbol)
        return self

class EpsilonNondeterministicFiniteAutomaton(NondeterministicFiniteAutomaton):

    def reset(self):
        self.current_state = self.epsilon_closure(set([self.start_state]))

    def epsilon_closure(self, states):
        state_list = list(states)
        state_set = set(states)
        for state in state_list:
            e_trans = set(self.transition(state, None, []))
            state_list += list(e_trans - state_set)
            state_set |= e_trans
        return state_set

    def read(self, symbol):
        self.current_state = self.epsilon_closure(
            self._transition_set(self.current_state, symbol)
        )
        return self



# Here Are some automatons for you to try out!
if __name__ == "__main__":
    D = DeterministicFiniteAutomaton(
        'q0',
        {
            #             0 |               1
            ('q0','0'): 'q2', ('q0','1'): 'q1', # q0
            ('q1','0'): 'q3', ('q1','1'): 'q0', # q1
            ('q2','0'): 'q0', ('q2','1'): 'q3', # q2
            ('q3','0'): 'q1', ('q3','1'): 'q2', # q3
        },
        ['q0']
    )

    H = NondeterministicFiniteAutomaton(
        1,
        {
            (1, 'w'): [1, 2],
            (1, 'e'): [1, 5],
            (1, 'b'): [1],
            (1, 'a'): [1],
            (1, 'y'): [1],
            (2, 'e'): [3],
            (3, 'b'): [4],
            (5, 'b'): [6],
            (6, 'a'): [7],
            (7, 'y'): [8],
        },
        [4, 8],
    )


    E = EpsilonNondeterministicFiniteAutomaton(
        1,
        {
            (1, None): [2, 4],
            (2, None): [3],
            (3, None): [6],
            (4, 'a'): [5],
            (5, 'b'): [6],
            (5, None): [7]
        },
        []
    )

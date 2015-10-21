def iter_hanoi(src, target, hold, size):
    if size > 1:
        for x in iter_hanoi(src, hold, target, size-1): yield x
    yield (src, target)
    if size > 1:
        for x in iter_hanoi(hold, target, src, size-1): yield x

def iter_hanoi_state(src, target, hold, size):
    def copy(state):
        return {k: list(v) for k,v in state.iteritems()}
    state = {src: list(range(size, 0, -1)), hold:[], target:[]}
    yield copy(state)
    for a, b in iter_hanoi(src, target, hold, size):
        item = state[a].pop()
        state[b].append(item)
        yield copy(state)

#get the state of the towers in log(idx) time.
def hanoi_state(src, target, hold, size, idx):
    
    def combine(a,b):
        """combines two dicts"""
        c = {}
        for key, value in a.items():
            c[key] = value
        for key, value in b.items():
            c[key].extend(value)
        return c

    assert idx <= hanoi_moves(size), "index {} out of range for size {}. Expected max index {}".format(idx, size, hanoi_moves(size))
    if size == 0: return {src: [], hold: [], target: []}
    else:
        median = (2 ** size) // 2
        is_in_first_stage = idx < median
        if is_in_first_stage: base = {src: [size], hold: [], target: []    }
        else:                 base = {src: [],     hold: [], target: [size]}
        
        if is_in_first_stage: rest = hanoi_state(src, hold, target, size-1, idx)
        else:                 rest = hanoi_state(hold, target, src, size-1, idx - median)
        return combine(base, rest)

hanoi_moves = lambda size: (2**size)-1

#verifies the correctness of hanoi_state
def test_state():
    size = 5
    for idx, state in enumerate(iter_hanoi_state(1, 3, 2, size)):
        assert state == hanoi_state_2(1, 3, 2, size, idx)

def hanoi_repr(state):
    sep = " "
    items = [val for tower in state.values() for val in tower]
    max_tower_size = sum(len(str(item)) for item in items) + len(sep)*(len(items)-1)
    ret = []
    for k in sorted(state.keys()):
        ret.append(sep.join(str(item) for item in state[k]).ljust(max_tower_size))
    return "|".join(ret)

if __name__ == "__main__":
    size = 16
    hanoi_moves = lambda size: (2**size)-1
    for i in range(hanoi_moves(size)+1):
        state = hanoi_state(1, 3, 2, size, i)
        print(hanoi_repr(state))
    #test_state()
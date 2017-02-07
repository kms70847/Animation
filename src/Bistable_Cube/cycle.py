from collections import defaultdict
from itertools import combinations

def graph_from_edge_tuples(edges):
    graph = defaultdict(set)
    for a,b in edges:
        graph[a].add(b)
        graph[b].add(a)
    return graph

def _iter_paths(graph, start, length, path=None):
    if path is None:
        path = [start]
    if length == 1:
        yield path
    else:
        for neighbor in graph[start]:
            if len(path) < 2 or path[-2] != neighbor:
                for x in _iter_paths(graph, neighbor, length-1, path + [neighbor]):
                    yield x

def _canonical(seq):
    """
    Rotates and flips a sequence into its minimal form.
    Useful for identifying node sequences that are identical except for starting point and direction.
    """
    def rotated(seq, i):
        return seq[i:] + seq[:i]
    def flipped(seq):
        return list(reversed(seq))
    candidates = []
    for i in range(len(seq)):
        for f in (flipped, lambda seq: seq):
            candidates.append(f(rotated(seq, i)))
    return tuple(min(candidates))

def get_minimal_cycles(graph):
    """
    detects all cycles of smallest size for a given graph.
    """
    nodes = list(graph)
    found = set()
    for i in range(3, len(graph)):
        for node in nodes:
            for path in _iter_paths(graph, node, i):
                if path[0] in graph[path[-1]]:
                    found.add(_canonical(path))
        if found:
            break
    return found
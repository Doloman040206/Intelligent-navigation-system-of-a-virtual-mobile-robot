import networkx as nx
from core.route_planner import _dijkstra


def test_dijkstra_finds_shortest_distance_path():
    graph = nx.MultiDiGraph()
    graph.add_node(1, x=0, y=0); graph.add_node(2, x=1, y=0); graph.add_node(3, x=2, y=0)
    graph.add_edge(1, 2, length=10); graph.add_edge(2, 3, length=10)
    graph.add_edge(1, 3, length=30)
    edges, cost = _dijkstra(graph, 1, 3, decision=None, adaptive=False)
    assert cost == 20
    assert len(edges) == 2

from heapq import heappush, heappop
from math import hypot
from time import perf_counter

from core.risk_model import edge_weight, edge_susceptibility


def _node_xy(graph, node):
    data = graph.nodes[node]
    return float(data["x"]), float(data["y"])


def _edge_length(graph, u, v, data):
    if data.get("length") is not None:
        return float(data["length"])

    x1, y1 = _node_xy(graph, u)
    x2, y2 = _node_xy(graph, v)

    return hypot(
        (x2 - x1) * 85000,
        (y2 - y1) * 111000,
    )


def _dijkstra(graph, source, target, decision=None, adaptive=True):
    queue = [(0.0, source)]

    distances = {source: 0.0}
    previous = {}
    visited = set()

    while queue:
        current_distance, u = heappop(queue)

        if u in visited:
            continue

        visited.add(u)

        if u == target:
            break

        for v, keyed_edges in graph.adj[u].items():
            for key, data in keyed_edges.items():
                length = _edge_length(graph, u, v, data)

                if adaptive:
                    if decision is None:
                        raise ValueError(
                            "Для адаптивного планування потрібна оцінка погоди"
                        )

                    cost = edge_weight(
                        length,
                        data,
                        decision,
                        adaptive=True,
                    )

                else:
                    cost = edge_weight(
                        length,
                        data,
                        {},
                        adaptive=False,
                    )

                candidate = current_distance + cost

                if candidate < distances.get(v, float("inf")):
                    distances[v] = candidate
                    previous[v] = (u, key, data)

                    heappush(queue, (candidate, v))

    if target not in distances:
        raise ValueError(
            "Маршрут не знайдено: граф не з'єднує початкову та цільову точки"
        )

    edges = []
    cursor = target

    while cursor != source:
        if cursor not in previous:
            raise ValueError("Не вдалося відновити маршрут")

        u, key, data = previous[cursor]

        edges.append((u, cursor, key, data))
        cursor = u

    edges.reverse()

    return edges, distances[target]


def _edge_coordinates(graph, u, v, data):
    geom = data.get("geometry")

    if geom is not None and hasattr(geom, "coords"):
        coords = [
            (float(y), float(x))
            for x, y in geom.coords
        ]

        ux, uy = _node_xy(graph, u)
        vx, vy = _node_xy(graph, v)

        if coords:
            d_forward = (
                (coords[0][0] - uy) ** 2
                + (coords[0][1] - ux) ** 2
            )

            d_reverse = (
                (coords[-1][0] - uy) ** 2
                + (coords[-1][1] - ux) ** 2
            )

            if d_reverse < d_forward:
                coords.reverse()

        return coords

    x1, y1 = _node_xy(graph, u)
    x2, y2 = _node_xy(graph, v)

    return [
        (y1, x1),
        (y2, x2),
    ]


def plan_route(graph, origin, destination, decision=None, adaptive=True):

    started = perf_counter()

    import osmnx as ox

    source = ox.distance.nearest_nodes(
        graph,
        X=origin[1],
        Y=origin[0],
    )

    target = ox.distance.nearest_nodes(
        graph,
        X=destination[1],
        Y=destination[0],
    )

    edges, total_cost = _dijkstra(
        graph,
        source,
        target,
        decision,
        adaptive,
    )

    coords = []
    total_length = 0.0
    weighted_risk_sum = 0.0

    for u, v, key, data in edges:
        length = _edge_length(graph, u, v, data)

        total_length += length

        if decision is not None:
            weighted_risk_sum += (
                length * edge_susceptibility(data, decision)
            )

        segment = _edge_coordinates(graph, u, v, data)

        if coords and segment and coords[-1] == segment[0]:
            coords.extend(segment[1:])
        else:
            coords.extend(segment)

    mean_risk = (
        weighted_risk_sum / total_length
        if total_length
        else 0.0
    )

    elapsed_ms = (perf_counter() - started) * 1000

    return {
        "coordinates": coords,
        "length_m": round(total_length, 2),
        "route_cost": round(total_cost, 2),
        "mode": (
            "weather_adaptive"
            if adaptive
            else "distance_baseline"
        ),
        "mean_segment_risk": round(mean_risk, 4),
        "planning_time_ms": round(elapsed_ms, 4),
        "edge_count": len(edges),
        "success": bool(coords),
    }
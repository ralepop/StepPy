from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from core.grid import Grid
from core.path import Path


@dataclass(slots=True)
class Agent:
    name: str

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        raise NotImplementedError


class ExampleAgent(Agent):

    def __init__(self):
        super().__init__("Example")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        while nodes[-1] != goal:
            r, c = nodes[-1]
            neighbors = grid.neighbors4(r, c)

            min_dist = min(grid.manhattan(t.pos, goal) for t in neighbors)
            best_tiles = [
                tile for tile in neighbors
                if grid.manhattan(tile.pos, goal) == min_dist
            ]
            best_tile = best_tiles[random.randint(0, len(best_tiles) - 1)]

            nodes.append(best_tile.pos)
            

        return Path(nodes)


class DFSAgent(Agent):

    def __init__(self):
        super().__init__("DFS")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        visited = {start}

        while nodes[-1] != goal:
            r, c = nodes[-1]

            neighbors = grid.neighbors4(r, c)

            for n in neighbors:
                if n.pos == goal:
                    nodes.append(n.pos)
                    return Path(nodes)

            unvisited_neighbors = [n for n in neighbors if n.pos not in visited]

            if not unvisited_neighbors:
                break

            min_cost = min(n.cost for n in unvisited_neighbors)

            best = next(n for n in unvisited_neighbors if n.cost == min_cost)

            visited.add(best.pos)
            nodes.append(best.pos)

        return Path(nodes)


class BranchAndBoundAgent(Agent):

    def __init__(self):
        super().__init__("BranchAndBound")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        counter = 0
        queue = [(0, 1, [start])] # cena, broj cvorova, putanja
        visited = {}

        while queue:
            queue.sort(key=lambda x: (x[0], x[1])) # prvo poredimo po ceni, zatim po broju cvorova

            cost, num_nodes, path = queue.pop(0)
            current = path[-1]

            if current == goal:
                return Path(path)
            
            if current in visited and visited[current] <= cost:
                continue
            
            visited[current] = cost

            r, c = current
            neighbors = grid.neighbors4(r, c)

            for n in neighbors:
                new_cost = cost + n.cost

                if n.pos not in visited or visited[n.pos] > new_cost:
                    counter += 1
                    queue.append((new_cost, num_nodes + 1, path + [n.pos]))
        
        return Path([start])



class AStar(Agent):

    def __init__(self):
        super().__init__("AStar")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        h_start = grid.manhattan(start, goal)
        
        queue = [(h_start, 0, 1, [start])]
        visited = {}

        while queue:
            queue.sort(key=lambda x: (x[0], x[2]))

            f_cost, g_cost, num_nodes, path = queue.pop(0)
            current = path[-1]

            if current == goal:
                return Path(path)
            
            if current in visited and visited[current] <= g_cost:
                continue

            visited[current] = g_cost

            r, c = current
            neighbors = grid.neighbors4(r, c)

            for n in neighbors:
                new_g = g_cost + n.cost
                new_h = grid.manhattan(n.pos, goal)
                new_f = new_g + new_h
                if n.pos not in visited or visited[n.pos] > new_g:
                    queue.append((new_f, new_g, num_nodes + 1, path + [n.pos]))
        
        return Path([start])
        



AGENTS: dict[str, Callable[[], Agent]] = {
    "Example": ExampleAgent,
    "DFS": DFSAgent,
    "BranchAndBound": BranchAndBoundAgent,
    "AStar": AStar
}


def create_agent(name: str) -> Agent:
    if name not in AGENTS:
        raise ValueError(f"Unknown agent '{name}'. Available: {', '.join(AGENTS.keys())}")
    return AGENTS[name]()

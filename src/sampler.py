import networkx as nx
import numpy as np
from queue import PriorityQueue
from torch_geometric.utils import subgraph
from torch_geometric.utils import to_networkx
from torch_geometric.data import Data
import torch 

def sample(graph : Data , n_samples : int, sample_size : int) -> list:

    G = to_networkx(graph)
    n_nodes = G.number_of_nodes()
    # list of nodes sorted by degree
    #init_nodes = sorted(G.nodes(), key=lambda x: G.degree(x), reverse=True)
    init_nodes = np.random.choice(n_nodes, n_samples, replace=False)

    samples = []
    for i in range(n_samples):
        queue = PriorityQueue()
        init = np.random.randint(n_nodes)

        queue.put_nowait((1, init))
        scores = {}
        scores[init_nodes[i]] = 1
        visited = set()

        while len(scores) < sample_size:
            if queue.empty():
                queue.put_nowait((1, np.random.randint(n_nodes)))
            score, node = queue.get_nowait()
            visited.add(node)
            neighbors = G.neighbors(node)
            for neighbor in neighbors:
                scores[neighbor] = scores.get(neighbor, 0) + 1
                if neighbor not in visited:
                    queue.put_nowait((scores[neighbor], neighbor))

        sample = subgraph(torch.tensor(list(scores.keys())), graph.edge_index, graph.edge_attr)
        samples.append(sample)

    return samples
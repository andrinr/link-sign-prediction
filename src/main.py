# External dependencies
import numpy as np 
import networkx as nx 
import matplotlib.pyplot as plt
import hydra
import pathlib
from omegaconf import DictConfig
# torch imports
import torch
import torch_geometric.transforms as T
from torch_geometric.loader import DataLoader
import pytorch_lightning as pl
from model.denoising import SignDenoising
# Local dependencies
from data.BSCLGraph import BSCLGraph
from data.SignedDataset import SignedDataset
from data.utils.samplers import even_exponential

@hydra.main(version_base=None, config_path="conf", config_name="config")
def DDSNG(cfg : DictConfig) -> None:

    BSCL_graph_kwargs = {
        "degree_generator": even_exponential,
        "degree_generator_kwargs": {"size": cfg.dataset.n_nodes, "scale": 5.0},
        "p_positive_sign": cfg.dataset.BSCL.p_positive,
        "p_close_triangle": cfg.dataset.BSCL.p_close_triangle,
        "p_close_for_balance": cfg.dataset.BSCL.p_close_for_balance,
        "remove_self_loops": cfg.dataset.BSCL.remove_self_loops
    }

    # We transorm the graph to a line graph, meaning each edge is replaced with a node
    # Signs are not node features and note edge features anymore
    transform = T.Compose([T.LineGraph])

    dataset = SignedDataset(
        graph_generator=BSCLGraph,
        graph_generator_kwargs=BSCL_graph_kwargs,
        transform=transform,
        num_graphs=cfg.dataset.n_graphs)

    dataloader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True,
    )
   
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SignDenoising().to(device)
    data = dataset[0].to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

    model.train()
    for epoch in range(200):
        optimizer.zero_grad()
        out = model(data)
        loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        optimizer.step()


if __name__ == "__main__":
    DDSNG()
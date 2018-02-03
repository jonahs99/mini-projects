import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np

class Network(nn.Module):
    def __init__(self, agent):
        super().__init__()
        self.n_bins = agent.n_bins
        self.conv = nn.Conv1d(4, 2, 4)
        self.fc = nn.Linear(2 * (self.n_bins - 3), 2)
        print(self)
    def forward(self, x):
        x = x.view(-1, 4, self.n_bins)
        x = nn.functional.relu(self.conv(x))
        x = x.view(-1, 2 * (self.n_bins - 3))
        x = self.fc(x)
        return x
    def create_input(self, agent):
        planes = torch.Tensor(4, agent.n_bins)
        for i in range(agent.n_bins):
            planes[0, i] = agent.eye_dist[i] / agent.sim.rad
            planes[1, i] = agent.eye_decay[i]
            planes[2, i] = agent.eye_r[i]
            planes[3, i] = agent.eye_g[i]
        return Variable(planes)
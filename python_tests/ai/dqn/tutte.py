import networkx as nx
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import random
import numpy as np
from collections import deque

# === PARAMETRI ===
num_colors = 3
episodes = 300
gamma = 0.9
epsilon = 0.2
lr = 0.001
batch_size = 64

# === CREA GRAFO DI TUTTE (3-REGOLARE PLANARE) ===
G = nx.tutte_graph()
edges = list(G.edges)
num_edges = len(edges)
edge_to_idx = {e: i for i, e in enumerate(edges)}
idx_to_edge = {i: e for e, i in edge_to_idx.items()}

# === RETE NEURALE ===
class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# === AMBIENTE ===
class EdgeColorEnv:
    def __init__(self, graph, num_colors):
        self.graph = graph
        self.num_colors = num_colors
        self.edges = list(graph.edges)
        self.reset()

    def reset(self):
        self.edge_colors = [-1] * len(self.edges)
        return self.get_state()

    def get_state(self):
        return np.array(self.edge_colors)

    def is_conflict(self, edge_idx, color):
        u, v = self.edges[edge_idx]
        for neighbor in self.graph[u]:
            e = (u, neighbor) if (u, neighbor) in edge_to_idx else (neighbor, u)
            if e in edge_to_idx:
                i = edge_to_idx[e]
                if self.edge_colors[i] == color:
                    return True
        for neighbor in self.graph[v]:
            e = (v, neighbor) if (v, neighbor) in edge_to_idx else (neighbor, v)
            if e in edge_to_idx:
                i = edge_to_idx[e]
                if self.edge_colors[i] == color:
                    return True
        return False

    def step(self, edge_idx, color):
        if self.edge_colors[edge_idx] != -1:
            return self.get_state(), -0.5, False
        conflict = self.is_conflict(edge_idx, color)
        self.edge_colors[edge_idx] = color
        reward = -1 if conflict else 1
        done = all(c != -1 for c in self.edge_colors)
        return self.get_state(), reward, done

# === AGENTE ===
class Agent:
    def __init__(self, state_size, action_size):
        self.model = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.memory = deque(maxlen=1000)

    def get_action(self, state):
        if random.random() < epsilon:
            edge_idx = random.randint(0, num_edges - 1)
            color = random.randint(0, num_colors - 1)
            return edge_idx * num_colors + color
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state)
            q_vals = self.model(state_tensor)
            return torch.argmax(q_vals).item()

    def remember(self, s, a, r, s_next, done):
        self.memory.append((s, a, r, s_next, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        for s, a, r, s_next, done in batch:
            print("Replay: " + str(s))
            q_val = self.model(torch.FloatTensor(s))[a]
            q_next = self.model(torch.FloatTensor(s_next)).max().detach()
            target = r + gamma * q_next * (1 - int(done))
            loss = (q_val - target) ** 2
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

# === ALLENAMENTO ===
env = EdgeColorEnv(G, num_colors)
agent = Agent(state_size=num_edges, action_size=num_edges * num_colors)

for e in range(episodes):
    state = env.reset()
    for _ in range(num_edges):
        action = agent.get_action(state)
        edge_idx = action // num_colors
        color = action % num_colors
        next_state, reward, done = env.step(edge_idx, color)
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        if done:
            break
    agent.replay(batch_size)

# === VISUALIZZA COLORE FINALE ===
final_colors = env.edge_colors
color_map = ['red', 'green', 'blue']
edge_colors = [color_map[c] if c != -1 else 'black' for c in final_colors]

pos = nx.planar_layout(G)
plt.figure(figsize=(10, 8))
nx.draw(G, pos, edge_color=edge_colors, node_color='lightgray', with_labels=True)
plt.title("Colorazione archi - Grafo di Tutte")
plt.show()

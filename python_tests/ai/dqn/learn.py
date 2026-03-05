import torch
import torch.nn as nn
import torch.optim as optim
import random
import networkx as nx
import numpy as np
from collections import deque

# Parameters
gamma = 0.9
epsilon = 0.1
learning_rate = 0.01
batch_size = 32
memory_size = 1000
num_episodes = 1000

# Genera un grafo 3-regolare con 1000 nodi
G = nx.random_regular_graph(d=3, n=1000)

print(f"Numero di nodi: {G.number_of_nodes()}")
print(f"Numero di archi: {G.number_of_edges()}")

# Verifica se è planare
is_planar, _ = nx.check_planarity(G)
print(f"È planare? {is_planar}")
exit()

nodes = list(G.nodes)

# Define state and action sizes
state_size = len(nodes)
action_size = state_size  # one possible action per node

# Neural Network
class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 32)
        self.fc2 = nn.Linear(32, action_size)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Agent class
class Agent:
    def __init__(self):
        self.model = DQN()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.memory = deque(maxlen=memory_size)

    def get_action(self, state):
        if random.random() < epsilon:
            return random.choice(nodes)
        with torch.no_grad():
            q_values = self.model(torch.FloatTensor(state))
            print(q_values)
            return torch.argmax(q_values).item()

    def remember(self, s, a, r, s_next):
        self.memory.append((s, a, r, s_next))

    def replay(self):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        for s, a, r, s_next in batch:
            target = r + gamma * torch.max(self.model(torch.FloatTensor(s_next))).item()
            output = self.model(torch.FloatTensor(s))[a]
            loss = (output - target) ** 2
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

# Helper functions
def one_hot(n, size):
    vec = [0] * size
    vec[n] = 1
    return vec

# Training loop
agent = Agent()
goal = 4  # target node

for e in range(num_episodes):
    current = random.choice(nodes)
    for t in range(10):  # limit steps
        state = one_hot(current, state_size)
        action = agent.get_action(state)
        reward = 1 if action == goal else -0.1
        next_state = one_hot(action, state_size)
        if not G.has_edge(current, action) and current != action:
            reward = -1  # penalty for invalid move
            next_state = state  # stay in same state
        agent.remember(state, action, reward, next_state)
        current = action if G.has_edge(current, action) else current
        if current == goal:
            break
    agent.replay()

print("Training finished.")

###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# History:
# - 06/Jan/2025 - Creation data
#
# TODOs:
# - TBD
#
# Done:
# - Template taken from: https://github.com/davidkerkkamp/DQN-GNN
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

import logging

import torch
from torch.nn import Linear
from torch_geometric.nn import GCNConv

import numpy as np

logger = logging.getLogger(__name__)


# Implementation of Double Deep Q-Network (DDQN)
class DQNAgent:

    # n_actions: number of actions that can be applied
    # input_shape: 2-tuple with input dimensions of feature matrix
    # gamma: reward discount factor
    # epsilon: threshold for epsilon-greedy learning strategy
    # replay_mem_size: size of replay buffer
    # replay_batch_size: batch size of memory replay
    # eps_min: minimum epsilon value
    # eps_dec: decrement epsilon with this value every step, until eps_min reached
    # replace_target_rate: number of steps after which target net should be updated
    # edge_index: adjacency matrix used in GNN
    # nn: neural net to use (gnn/fc)
    def __init__(self, n_actions, input_shape, gamma=0.99, epsilon=1.0, replay_mem_size=500, replay_batch_size=32, eps_min=0.05, eps_dec=1e-4, replace_target_rate=10, edge_index=None, nn='gnn'):
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # random action selection probability
        self.n_actions = n_actions  # number of actions
        self.action_space = [i for i in range(n_actions)]
        self.input_shape = input_shape  # shape of state observations
        self.replay_mem_size = replay_mem_size  # size of experience replay buffer
        self.replay_batch_size = replay_batch_size  # size of replay batches
        self.eps_min = eps_min
        self.eps_dec = eps_dec
        self.replace_target_rate = replace_target_rate  # number of steps after which target net weights are updated
        self.update_step_counter = 0

        self.replay_memory = ReplayMemory(self.replay_mem_size, self.input_shape)
        if nn == 'gnn':
            self.net = GraphNet(n_features=self.input_shape[1], n_actions=self.n_actions, edge_index=edge_index)
            self.target_net = GraphNet(n_features=self.input_shape[1], n_actions=self.n_actions, edge_index=edge_index)
        # Alternatively, use fully connected linear instead of GNN
        elif nn == 'fc':
            self.net = SimpleLinear(n_features=self.input_shape[1], n_actions=self.n_actions)
            self.target_net = SimpleLinear(n_features=self.input_shape[1], n_actions=self.n_actions)
        else:
            raise Exception(f'Unknown nn type "{nn}"')

    def store_transition(self, s, a, r, s_next, done):
        self.replay_memory.store_transition(s, a, r, s_next, done)

    def sample_memory(self):
        states, actions, rewards, next_states, dones = self.replay_memory.sample(self.replay_batch_size)
        states = torch.tensor(states).to(self.net.device)
        rewards = torch.tensor(rewards).to(self.net.device)
        dones = torch.tensor(dones).to(self.net.device)
        actions = torch.tensor(actions).to(self.net.device)
        next_states = torch.tensor(next_states).to(self.net.device)
        return states, actions, rewards, next_states, dones

    def decrement_epsilon(self):
        new_eps = self.epsilon - self.eps_dec
        self.epsilon = new_eps if new_eps >= self.eps_min else self.eps_min

    # Select action during training, using epsilon-greedy strategy
    def select_action(self, state):
        if np.random.random() > self.epsilon:  # Select actions using net
            state = torch.tensor(state).to(self.net.device)
            action_values = self.net(state)
            return torch.argmax(action_values, dim=1).cpu().detach().numpy()
        else:  # Random actions
            return np.random.choice(self.action_space, size=len(state))

    # Select action after training
    def predict(self, state):
        state = torch.tensor(state).to(self.net.device)
        action_values = self.net(state)
        return torch.argmax(action_values, dim=1).cpu().detach().numpy()

    # Apply a learning/optimization step
    def update_network(self):
        if self.replay_memory.counter < self.replay_mem_size:  # Don't update if replay buffer isn't filled yet
            return

        self.net.opt.zero_grad()
        self.update_target_network()
        states, actions, rewards, next_states, done_mask = self.sample_memory()

        q_pred_all = self.net(states)
        pipe_indices = np.arange(q_pred_all.shape[1])
        # q_pred = torch.as_tensor(np.zeros((q_pred_all.shape[0], q_pred_all.shape[1])).astype('float32'))
        q_pred = torch.zeros((q_pred_all.shape[0], q_pred_all.shape[1]))
        for i, pred in enumerate(q_pred_all):
            q_pred[i] = pred[pipe_indices, actions[i]]
        q_next = self.target_net(next_states)
        q_eval = self.net(next_states)

        max_actions = torch.argmax(q_eval, dim=2)
        q_next[done_mask] = 0  # For terminal states, there is no future reward

        # q_target = torch.as_tensor(np.zeros((q_pred_all.shape[0], q_pred_all.shape[1])).astype('float32'))
        q_target = torch.zeros((q_pred_all.shape[0], q_pred_all.shape[1]))
        for i, q in enumerate(q_next):
            q_target[i] = rewards[i] + self.gamma * q[pipe_indices, max_actions[i]]

        loss = self.net.loss(q_target, q_pred).to(self.net.device)
        loss.backward()
        self.net.opt.step()
        self.update_step_counter += 1
        self.decrement_epsilon()

    def update_target_network(self):
        if self.update_step_counter % self.replace_target_rate == 0:
            self.target_net.load_state_dict(self.net.state_dict())  # Replace target net params

    def save_model(self, path, run_id):
        self.target_net.save_model(f'{path}/target-model-{run_id}.torch')
        self.net.save_model(f'{path}/model-{run_id}.torch')

    def load_model(self, path, net=1):
        if net == 1:
            self.net.load_model(path)
        else:
            self.target_net.load_model(path)

    def load_checkpoint(self, path):
        checkpoint = torch.load(path)
        self.epsilon = checkpoint['epsilon']
        self.replay_memory.load_state_dict(checkpoint['replay_memory'])
        self.net.load_state_dict(checkpoint['net']['model_state_dict'])
        self.net.opt.load_state_dict(checkpoint['net']['optimizer_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net']['model_state_dict'])
        self.net.train()
        self.target_net.train()
        print(f"Checkpoint loaded: episode {checkpoint['episode']}, epsilon: {checkpoint['epsilon']}")
        return checkpoint['episode'], checkpoint['stats']
    

# Replay memory for Deep Q-Network
class ReplayMemory:
    def __init__(self, mem_size, input_shape):
        self.mem_size = mem_size
        self.index = 0
        self.counter = 0

        self.state_memory = np.zeros((self.mem_size, *input_shape), dtype=np.float32)
        self.next_state_memory = np.zeros((self.mem_size, *input_shape), dtype=np.float32)
        self.action_memory = np.zeros((self.mem_size, input_shape[0]), dtype=np.int64)
        self.reward_memory = np.zeros((self.mem_size, input_shape[0]), dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

    def store_transition(self, s, a, r, s_next, done):
        self.state_memory[self.index] = s
        self.next_state_memory[self.index] = s_next
        self.action_memory[self.index] = a
        self.reward_memory[self.index] = r
        self.terminal_memory[self.index] = done
        self.index = (self.index + 1) % self.mem_size
        self.counter += 1

    def sample(self, batch_size):
        batch_i = np.random.choice(self.mem_size, batch_size, replace=False)
        states = self.state_memory[batch_i]
        actions = self.action_memory[batch_i]
        rewards = self.reward_memory[batch_i]
        next_states = self.next_state_memory[batch_i]
        dones = self.terminal_memory[batch_i]
        return states, actions, rewards, next_states, dones

    def state_dict(self):
        return {
            'mem_size': self.mem_size,
            'index': self.index,
            'counter': self.counter,
            'state_memory': self.state_memory,
            'next_state_memory': self.next_state_memory,
            'action_memory': self.action_memory,
            'reward_memory': self.reward_memory,
            'terminal_memory': self.terminal_memory,
        }

    def load_state_dict(self, state_dict):
        self.mem_size = state_dict['mem_size']
        self.index = state_dict['index']
        self.counter = state_dict['counter']
        self.state_memory = state_dict['state_memory']
        self.next_state_memory = state_dict['next_state_memory']
        self.action_memory = state_dict['action_memory']
        self.reward_memory = state_dict['reward_memory']
        self.terminal_memory = state_dict['terminal_memory']


class GraphNet(torch.nn.Module):
    def __init__(self, n_features, n_actions, emb_size=32, edge_index=None):
        super(GraphNet, self).__init__()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.edge_index = edge_index.to(self.device)
        self.conv1 = GCNConv(n_features, emb_size)
        self.conv2 = GCNConv(emb_size, emb_size)
        self.fc = Linear(emb_size, n_actions)

        self.opt = torch.optim.AdamW(self.parameters(), lr=0.001, weight_decay=0.01)
        self.loss = torch.nn.MSELoss()
        self.to(self.device)

    def set_edge_index(self, edge_index):
        self.edge_index = edge_index

    def forward(self, x):
        assert self.edge_index is not None, "Edge indices have not been set, use 'set_edge_index(edge_index)'"
        # data = Data(x=x, edge_index=self.edge_index)
        x = self.conv1(x, self.edge_index)
        x = x.relu()
        x = self.fc(self.conv2(x, self.edge_index))
        return x

    def save_model(self, path):
        torch.save(self.cpu().state_dict(), path)

    def load_model(self, path):
        self.load_state_dict(torch.load(path))
        self.eval()


class SimpleLinear(torch.nn.Module):
    def __init__(self, n_features, n_actions):
        super(SimpleLinear, self).__init__()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.fc = Linear(n_features, n_actions)
        self.opt = torch.optim.AdamW(self.parameters(), lr=0.001, weight_decay=0.01)
        self.loss = torch.nn.MSELoss()
        self.to(self.device)

    def forward(self, x):
        return self.fc(x)

    def save_model(self, path):
        torch.save(self.cpu().state_dict(), path)

    def load_model(self, path):
        self.load_state_dict(torch.load(path))
        self.eval()
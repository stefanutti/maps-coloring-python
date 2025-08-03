import gym
import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# Suppress the numpy deprecation warning
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create the CartPole environment
env = gym.make("CartPole-v1", render_mode=None)

# Neural network model for approximating Q-values
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class PrioritizedReplay:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.priorities = []
        
    def push(self, transition, priority=None):
        if priority is None:
            priority = max(self.priorities) if self.priorities else 1.0
        
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)
            self.priorities.pop(0)
            
        self.memory.append(transition)
        self.priorities.append(priority)
    
    def sample(self, batch_size):
        probs = np.array(self.priorities) / sum(self.priorities)
        indices = np.random.choice(len(self.memory), batch_size, p=probs)
        samples = [self.memory[idx] for idx in indices]
        return samples
    
    def __len__(self):
        return len(self.memory)

# Hyperparameters
learning_rate = 0.001
gamma = 0.99
epsilon = 1.0
epsilon_min = 0.01
epsilon_decay = 0.995
batch_size = 64
target_update_freq = 1000
memory_size = 10000
episodes = 1000

# Initialize Q-networks
input_dim = env.observation_space.shape[0]
output_dim = env.action_space.n
policy_net = DQN(input_dim, output_dim).to(device)
target_net = DQN(input_dim, output_dim).to(device)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.Adam(policy_net.parameters(), lr=learning_rate)
memory = PrioritizedReplay(memory_size)

def select_action(state, epsilon):
    if random.random() < epsilon:
        return env.action_space.sample()
    else:
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        with torch.no_grad():
            q_values = policy_net(state)
        return torch.argmax(q_values).item()

def optimize_model():
    if len(memory) < batch_size:
        return None
    
    try:
        batch = memory.sample(batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

        # Convert to numpy arrays first, then to tensors
        state_batch = np.array(state_batch, dtype=np.float32)
        next_state_batch = np.array(next_state_batch, dtype=np.float32)
        
        # Convert to tensors
        state_batch = torch.from_numpy(state_batch).to(device)
        action_batch = torch.tensor(action_batch, dtype=torch.long).unsqueeze(1).to(device)
        reward_batch = torch.tensor(reward_batch, dtype=torch.float).to(device)
        next_state_batch = torch.from_numpy(next_state_batch).to(device)
        done_batch = torch.tensor(done_batch, dtype=torch.float).to(device)

        # Compute Q-values for current states
        q_values = policy_net(state_batch).gather(1, action_batch).squeeze()

        # Compute target Q-values using the target network
        with torch.no_grad():
            max_next_q_values = target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + gamma * max_next_q_values * (1 - done_batch)

        loss = nn.MSELoss()(q_values, target_q_values)

        optimizer.zero_grad()
        loss.backward()
        
        # Add gradient clipping
        torch.nn.utils.clip_grad_norm_(policy_net.parameters(), max_norm=1.0)
        
        optimizer.step()
        return loss.item()
    except Exception as e:
        print(f"Error during optimization: {e}")
        return None

# Main training loop
rewards_per_episode = []
steps_done = 0

try:
    for episode in range(episodes):
        state, _ = env.reset()
        state = np.array(state, dtype=np.float32)
        assert len(state.shape) == 1, f"Unexpected state shape: {state.shape}"
        
        episode_reward = 0
        done = False
        truncated = False
        
        while not (done or truncated):
            # Select action
            action = select_action(state, epsilon)
            next_state, reward, done, truncated, _ = env.step(action)  # Updated step call
            next_state = np.array(next_state, dtype=np.float32)
            
            # Store transition in memory
            memory.push((state, action, reward, next_state, done))
            
            # Update state
            state = next_state
            episode_reward += reward
            
            # Optimize model
            loss = optimize_model()
            
            # Update target network periodically
            if steps_done % target_update_freq == 0:
                target_net.load_state_dict(policy_net.state_dict())

            steps_done += 1

        # Decay epsilon
        epsilon = max(epsilon_min, epsilon_decay * epsilon)
        
        rewards_per_episode.append(episode_reward)
        
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(rewards_per_episode[-10:])
            print(f"Episode {episode + 1}, Average Reward (last 10): {avg_reward:.2f}")

except KeyboardInterrupt:
    print("\nTraining interrupted by user")
except Exception as e:
    print(f"Error during training: {e}")
finally:
    env.close()

# Plotting the rewards per episode
plt.figure(figsize=(10, 6))
plt.plot(rewards_per_episode)
plt.xlabel('Episode')
plt.ylabel('Reward')
plt.title('DQN on CartPole')
plt.grid(True)
plt.show()
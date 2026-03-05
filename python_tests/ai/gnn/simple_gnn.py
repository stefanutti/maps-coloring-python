import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data

# 1) Define a small example graph.
#    Here, we create a simple 4-node cycle: 0 -> 1 -> 2 -> 3 -> 0.

# Edge indices in a 2 x E tensor:
edge_index = torch.tensor([
    [0, 1, 1, 2, 2, 3, 3, 0],  # Source nodes
    [1, 0, 2, 1, 3, 2, 0, 3]   # Target nodes
], dtype=torch.long)

# Node feature matrix: x[i] is the feature vector of node i.
# Here, let's just give each node a single scalar feature.
x = torch.tensor([
    [1.0],  # Node 0
    [2.0],  # Node 1
    [3.0],  # Node 2
    [4.0]   # Node 3
], dtype=torch.float)

# Node labels (for demonstration). Suppose we want to classify
# nodes into two classes: 0 or 1.
y = torch.tensor([0, 1, 0, 1], dtype=torch.long)

# Create a PyG Data object
data = Data(x=x, edge_index=edge_index, y=y)

# 2) Define a simple Graph Convolutional Network (GCN).
class SimpleGCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(SimpleGCN, self).__init__()
        # Two GCN layers
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        # First GCN layer + ReLU
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        # Second GCN layer (no activation here; we feed it to softmax/cross-entropy)
        x = self.conv2(x, edge_index)
        return x

# Instantiate the GCN model
model = SimpleGCN(in_channels=1, hidden_channels=2, out_channels=2)

# 3) Define an optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# 4) Training loop
for epoch in range(50):
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)  # Forward pass
    loss = F.cross_entropy(out, data.y)   # Compare predictions vs. true labels
    loss.backward()                       # Backprop
    optimizer.step()                      # Update parameters
    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

# 5) Evaluate the model
out = model(data.x, data.edge_index)
pred = out.argmax(dim=1)   # Predicted class per node
print("Final Predictions:", pred.tolist())
print("True Labels      :", data.y.tolist())

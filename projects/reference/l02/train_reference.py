import numpy as np
from network_reference import TinyNetwork

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([[0.0], [1.0], [1.0], [0.0]])

model = TinyNetwork(seed=7)
model.forward(X)
start_loss = model.loss(y)
loss_history = [start_loss]
for _ in range(2000):
    model.forward(X)
    model.backward_and_step(y, learning_rate=0.2)
    model.forward(X)
    loss_history.append(model.loss(y))
end_loss = loss_history[-1]
predictions = model.predict(X).reshape(-1)
accuracy = float(np.mean(predictions == y.reshape(-1)))
print(f"start_loss={start_loss:.6f}")
print(f"end_loss={end_loss:.6f}")
print(f"accuracy={accuracy:.3f}")
print("predictions=", predictions.tolist())

import numpy as np
from network import TinyNetwork

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([[0.0], [1.0], [1.0], [0.0]])

model = TinyNetwork(seed=7)
model.forward(X)
start_loss = model.loss(y)

for _ in range(2000):
    model.forward(X)
    model.backward_and_step(y, learning_rate=0.2)

model.forward(X)
end_loss = model.loss(y)
predictions = model.predict(X).reshape(-1)

print(f"start_loss={start_loss:.6f}")
print(f"end_loss={end_loss:.6f}")
print("predictions=", predictions.tolist())

if end_loss >= start_loss * 0.95:
    print("STARTER STATUS: no meaningful learning yet; implement backward_and_step.")
else:
    print("TRAINING STATUS: loss decreased; run the submission checker.")

import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

class TinyNetwork:
    def __init__(self, seed=7):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, 0.5, size=(2, 4))
        self.b1 = np.zeros(4)
        self.W2 = rng.normal(0.0, 0.5, size=(4, 1))
        self.b2 = np.zeros(1)

    def forward(self, X):
        self.X = X
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.probs = sigmoid(self.z2)
        return self.probs

    def loss(self, y):
        eps = 1e-7
        p = np.clip(self.probs, eps, 1.0 - eps)
        return float(-np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))

    def backward_and_step(self, y, learning_rate=0.2):
        # TODO: implement explicit gradients for W2, b2, W1, and b1,
        # then update each parameter with gradient descent.
        # Keep array shapes unchanged and average gradients over the batch.
        return None

    def predict(self, X):
        return (self.forward(X) >= 0.5).astype(int)

"""Starter for p03-transfer-learning.

Complete build_frozen_transfer() and fine_tune() without changing the fixed
dataset split or validation set. The clean starter runs and stops at the
visible TODO boundary rather than hiding a failure.
"""
from __future__ import annotations
import copy
import random
import numpy as np
import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

SEED = 13
LOOP_DIGITS = np.array([0, 6, 8, 9])

def seed_all(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)

class Encoder(torch.nn.Module):
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.net = torch.nn.Sequential(torch.nn.Linear(64, hidden), torch.nn.ReLU())
    def forward(self, x):
        return self.net(x)

class SourceModel(torch.nn.Module):
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.encoder = Encoder(hidden)
        self.head = torch.nn.Linear(hidden, 10)
    def forward(self, x):
        return self.head(self.encoder(x))

class TargetModel(torch.nn.Module):
    def __init__(self, encoder=None, hidden: int = 32):
        super().__init__()
        self.encoder = encoder if encoder is not None else Encoder(hidden)
        self.head = torch.nn.Linear(hidden, 2)
    def forward(self, x):
        return self.head(self.encoder(x))

def load_data():
    digits = load_digits()
    X = digits.data.astype("float32") / 16.0
    y = digits.target.astype("int64")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.25, random_state=SEED, stratify=y
    )
    target_train = np.isin(y_train, LOOP_DIGITS).astype("int64")
    target_val = np.isin(y_val, LOOP_DIGITS).astype("int64")
    idx = np.arange(len(y_train))
    small_idx, _ = train_test_split(
        idx, train_size=40, random_state=SEED, stratify=target_train
    )
    return {
        "source_X": torch.tensor(X_train),
        "source_y": torch.tensor(y_train),
        "target_X": torch.tensor(X_train[small_idx]),
        "target_y": torch.tensor(target_train[small_idx]),
        "val_X": torch.tensor(X_val),
        "val_source_y": torch.tensor(y_val),
        "val_target_y": torch.tensor(target_val),
    }

def train_classifier(model, X, y, *, epochs: int, lr: float):
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=lr)
    loss_fn = torch.nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = loss_fn(model(X), y)
        loss.backward()
        optimizer.step()
    return model

def accuracy(model, X, y) -> float:
    model.eval()
    with torch.no_grad():
        return float((model(X).argmax(1) == y).float().mean())

def pretrain_source(data):
    seed_all()
    model = SourceModel()
    return train_classifier(model, data["source_X"], data["source_y"], epochs=120, lr=0.1)

def build_scratch(data):
    seed_all()
    model = TargetModel()
    return train_classifier(model, data["target_X"], data["target_y"], epochs=200, lr=0.2)

def build_frozen_transfer(source, data):
    # TODO 1: copy source.encoder, freeze it, attach a new two-class head,
    # then train only that head on the fixed 40-example target set.
    raise NotImplementedError("TODO: implement frozen transfer")

def fine_tune(frozen_model, data, *, lr: float = 0.01):
    # TODO 2: start from a COPY of frozen_model, unfreeze encoder parameters,
    # and fine-tune on the same target examples using the supplied learning rate.
    raise NotImplementedError("TODO: implement controlled fine-tuning")

def main():
    data = load_data()
    source = pretrain_source(data)
    scratch = build_scratch(data)
    print(f"source_accuracy={accuracy(source, data['val_X'], data['val_source_y']):.3f}")
    print(f"scratch_accuracy={accuracy(scratch, data['val_X'], data['val_target_y']):.3f}")
    try:
        frozen = build_frozen_transfer(source, data)
        fine = fine_tune(frozen, data)
        print(f"frozen_accuracy={accuracy(frozen, data['val_X'], data['val_target_y']):.3f}")
        print(f"fine_tuned_accuracy={accuracy(fine, data['val_X'], data['val_target_y']):.3f}")
    except NotImplementedError as exc:
        print(exc)
        print("Starter is healthy. Complete the two visible TODOs, then run the checker.")

if __name__ == "__main__":
    main()

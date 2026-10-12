from __future__ import annotations
import copy, random
import numpy as np
import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

SEED=13
LOOP_DIGITS=np.array([0,6,8,9])

def seed_all():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.set_num_threads(1)

class Encoder(torch.nn.Module):
    def __init__(self, hidden=32):
        super().__init__(); self.net=torch.nn.Sequential(torch.nn.Linear(64,hidden),torch.nn.ReLU())
    def forward(self,x): return self.net(x)

class SourceModel(torch.nn.Module):
    def __init__(self):
        super().__init__(); self.encoder=Encoder(); self.head=torch.nn.Linear(32,10)
    def forward(self,x): return self.head(self.encoder(x))

class TargetModel(torch.nn.Module):
    def __init__(self,encoder=None):
        super().__init__(); self.encoder=encoder if encoder is not None else Encoder(); self.head=torch.nn.Linear(32,2)
    def forward(self,x): return self.head(self.encoder(x))

def load_data():
    d=load_digits(); X=d.data.astype('float32')/16.0; y=d.target.astype('int64')
    Xt,Xv,yt,yv=train_test_split(X,y,test_size=0.25,random_state=SEED,stratify=y)
    tt=np.isin(yt,LOOP_DIGITS).astype('int64'); tv=np.isin(yv,LOOP_DIGITS).astype('int64')
    idx=np.arange(len(yt)); small,_=train_test_split(idx,train_size=40,random_state=SEED,stratify=tt)
    return {'source_X':torch.tensor(Xt),'source_y':torch.tensor(yt),'target_X':torch.tensor(Xt[small]),'target_y':torch.tensor(tt[small]),'val_X':torch.tensor(Xv),'val_source_y':torch.tensor(yv),'val_target_y':torch.tensor(tv)}

def train_classifier(model,X,y,epochs,lr):
    opt=torch.optim.SGD([p for p in model.parameters() if p.requires_grad],lr=lr); lossf=torch.nn.CrossEntropyLoss(); model.train()
    for _ in range(epochs):
        opt.zero_grad(); loss=lossf(model(X),y); loss.backward(); opt.step()
    return model

def accuracy(model,X,y):
    model.eval()
    with torch.no_grad(): return float((model(X).argmax(1)==y).float().mean())

def pretrain_source(data):
    seed_all(); return train_classifier(SourceModel(),data['source_X'],data['source_y'],120,0.1)

def build_scratch(data):
    seed_all(); return train_classifier(TargetModel(),data['target_X'],data['target_y'],200,0.2)

def build_frozen_transfer(source,data):
    encoder=copy.deepcopy(source.encoder)
    for p in encoder.parameters(): p.requires_grad=False
    seed_all(); return train_classifier(TargetModel(encoder),data['target_X'],data['target_y'],200,0.2)

def fine_tune(frozen,data,lr=0.01):
    model=copy.deepcopy(frozen)
    for p in model.encoder.parameters(): p.requires_grad=True
    return train_classifier(model,data['target_X'],data['target_y'],80,lr)

def encoder_vector(model):
    return torch.cat([p.detach().flatten() for p in model.encoder.parameters()])

def noisy_slice_accuracy(model,data,sigma=0.35):
    rng=np.random.default_rng(SEED); noise=rng.normal(0.0,sigma,size=data['val_X'].shape).astype('float32'); noisy=torch.clamp(data['val_X']+torch.tensor(noise),0.0,1.0)
    return accuracy(model,noisy,data['val_target_y'])

def run_reference():
    data=load_data(); source=pretrain_source(data); scratch=build_scratch(data); frozen=build_frozen_transfer(source,data); before=encoder_vector(frozen).clone(); fine=fine_tune(frozen,data,0.01); aggressive=fine_tune(frozen,data,1.0)
    return {'source_accuracy':accuracy(source,data['val_X'],data['val_source_y']),'scratch_accuracy':accuracy(scratch,data['val_X'],data['val_target_y']),'frozen_accuracy':accuracy(frozen,data['val_X'],data['val_target_y']),'fine_accuracy':accuracy(fine,data['val_X'],data['val_target_y']),'aggressive_accuracy':accuracy(aggressive,data['val_X'],data['val_target_y']),'fine_movement':float(torch.linalg.vector_norm(encoder_vector(fine)-before)),'aggressive_movement':float(torch.linalg.vector_norm(encoder_vector(aggressive)-before)),'noisy_accuracy':noisy_slice_accuracy(fine,data)}

if __name__=='__main__':
    for key,value in run_reference().items(): print(f'{key}={value:.3f}')

from __future__ import annotations
import importlib.util
import pathlib
import sys
import torch

def load_module(path):
    spec=importlib.util.spec_from_file_location('submission_adaptation',path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def fail(message):
    print(f'FAIL: {message}'); raise SystemExit(1)

def main():
    if len(sys.argv)!=2: fail('usage: check_submission.py <projects/starters/l03>')
    root=pathlib.Path(sys.argv[1]); path=root/'adaptation.py'
    if not path.exists(): fail(f'missing {path}')
    mod=load_module(path); data=mod.load_data(); source=mod.pretrain_source(data); scratch=mod.build_scratch(data)
    try:
        frozen=mod.build_frozen_transfer(source,data); before=torch.cat([p.detach().flatten() for p in frozen.encoder.parameters()]).clone(); fine=mod.fine_tune(frozen,data,lr=0.01); aggressive=mod.fine_tune(frozen,data,lr=1.0)
    except NotImplementedError as exc: fail(str(exc))
    frozen_after=torch.cat([p.detach().flatten() for p in frozen.encoder.parameters()]); fine_vec=torch.cat([p.detach().flatten() for p in fine.encoder.parameters()]); aggressive_vec=torch.cat([p.detach().flatten() for p in aggressive.encoder.parameters()])
    source_acc=mod.accuracy(source,data['val_X'],data['val_source_y']); scratch_acc=mod.accuracy(scratch,data['val_X'],data['val_target_y']); frozen_acc=mod.accuracy(frozen,data['val_X'],data['val_target_y']); fine_acc=mod.accuracy(fine,data['val_X'],data['val_target_y']); fine_move=float(torch.linalg.vector_norm(fine_vec-before)); aggressive_move=float(torch.linalg.vector_norm(aggressive_vec-before))
    if source_acc<=0.80: fail(f'source accuracy too low: {source_acc:.3f}')
    if min(scratch_acc,frozen_acc,fine_acc)<=0.75: fail(f'target accuracy too low: scratch={scratch_acc:.3f}, frozen={frozen_acc:.3f}, fine={fine_acc:.3f}')
    if any(p.requires_grad for p in frozen.encoder.parameters()): fail('frozen encoder still has trainable parameters')
    if not torch.equal(before,frozen_after): fail('frozen encoder changed during head training')
    if fine_move<=0: fail('fine-tuning did not move encoder parameters')
    if aggressive_move<=fine_move*2: fail('aggressive failure did not move encoder substantially more than conservative fine-tuning')
    print('PASS'); print(f'source_accuracy={source_acc:.3f}'); print(f'scratch_accuracy={scratch_acc:.3f}'); print(f'frozen_accuracy={frozen_acc:.3f}'); print(f'fine_accuracy={fine_acc:.3f}'); print(f'fine_movement={fine_move:.3f}'); print(f'aggressive_movement={aggressive_move:.3f}')

if __name__=='__main__': main()

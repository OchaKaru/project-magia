from torch.nn import Sequential
from torch.utils.checkpoint import checkpoint

class CheckPointed(Sequential): # using checkpointed backprop for memory efficiency
    def forward(self, *args):
        return checkpoint(super().forward, *args)
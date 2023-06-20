from util.checkpointed import CheckPointed
from torch.nn import Module, Linear, ReLU, Dropout

class FeedForward(Module):
  # simple linear layer
    def __init__(self, n_embed):
        super().__init__()
        self.seq = CheckPointed(
            Linear(n_embed, 4 * n_embed), # adding more computation by multiplying by 4
            ReLU(),
            Linear(4 * n_embed, n_embed), # we need projection layers to finalize the projection onto the residual pathway
            Dropout(dropout), # adding drop out to prevent overfitting
        )

    def forward(self, x):
        return self.seq(x)
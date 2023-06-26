from util.checkpointed import CheckPointed
from torch.nn import Module, Linear, ReLU, Dropout

class FeedForward(Module):
  # simple linear layer
    def __init__(self, number_of_embeddings: int, dropout_rate: float = 0.4):
        super().__init__()
        self.seq = CheckPointed(
            Linear(number_of_embeddings, 4 * number_of_embeddings), # adding more computation by multiplying by 4
            ReLU(),
            Linear(4 * number_of_embeddings, number_of_embeddings), # we need projection layers to finalize the projection onto the residual pathway
            Dropout(dropout_rate) # adding drop out to prevent overfitting
        )

    def forward(self, x):
        return self.seq(x)
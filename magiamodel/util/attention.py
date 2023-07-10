from torch import autocast, cat, tril, ones, float32, cuda
from torch.nn.functional import softmax
from torch.nn import Module, ModuleList, Linear, Dropout

class SelfAttentionHead(Module):
    # one head of self attention
    def __init__(self, number_of_embeddings: int, head_size: int, block_size: int, dropout_rate: float, device: str = 'cpu'):
        super().__init__()
        self.key = Linear(number_of_embeddings, head_size, bias = False)
        self.query = Linear(number_of_embeddings, head_size, bias = False)
        self.value = Linear(number_of_embeddings, head_size, bias = False)
        self.register_buffer('tril', tril(ones(block_size, block_size)))
        self.device = device
        self.dropout = Dropout(dropout_rate) # adding drop out to prevent overfitting

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        # compute attention scores
        weight = q @ k.transpose(-2, -1) * k.shape[-1]**-0.5 # (B, T, head_size) @ (B, head_size, T) -> (B, T, T)
        weight = weight.masked_fill(self.tril[:T][:T] == 0, float('-inf')) # (B, T, T)

        with autocast(device_type = self.device, enabled = False):
            weight = softmax(weight, dim = -1)
        weight = self.dropout(weight)
        # perform the weighted aggregation
        v = self.value(x) # (B, T, C)
        out = weight @ v # (B, T, T) @ (B, T, C) -> (B, T, C)

        return out
    
class MultiSelfAttentionHead(Module):
    # the hydra of self attention
    def __init__(self, number_of_embeddings: int, head_size: int, block_size: int, number_of_heads: int, dropout_rate: float, device: str = 'cpu'):
        super().__init__()
        self.heads = ModuleList([SelfAttentionHead(number_of_embeddings, head_size, block_size, dropout_rate, device = device) for _ in range(number_of_heads)])
        self.proj = Linear(head_size * number_of_heads, number_of_embeddings) # we need projection layers to finalize the projection onto the residual pathway
        self.dropout = Dropout(dropout_rate) # adding drop out to prevent overfitting

    def forward(self, x):
        out = cat([h(x) for h in self.heads], dim = - 1)
        out = self.dropout(self.proj(out))
        return out
from torch import autocast, cat
from torch.nn.functional import softmax
from torch.nn import Module, ModuleList, Linear, Dropout

class SelfAttentionHead(Module):
    # one head of self attention
    def __init__(self, head_size):
        super().__init__()
        self.key = Linear(n_embed, head_size, bias = False)
        self.query = Linear(n_embed, head_size, bias = False)
        self.value = Linear(n_embed, head_size, bias = False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = Dropout(dropout) # adding drop out to prevent overfitting

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        # compute attention scores
        weight = q @ k.transpose(-2, -1) * k.shape[-1]**-0.5 # (B, T, head_size) @ (B, head_size, T) -> (B, T, T)
        weight = weight.masked_fill(self.tril[:T][:T] == 0, float('-inf')) # (B, T, T)

        with autocast(device_type = device, dtype = torch.float32):
            weight = softmax(weight, dim = -1)
        weight = self.dropout(weight)
        # perform the weighted aggregation
        v = self.value(x) # (B, T, C)
        out = weight @ v # (B, T, T) @ (B, T, C) -> (B, T, C)

        return out
    
class MultiSelfAttentionHead(nn.Module):
    # the hydra of self attention
    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = ModuleList([SelfAttentionHead(head_size) for _ in range(num_heads)])
        self.proj = Linear(head_size * num_heads, n_embed) # we need projection layers to finalize the projection onto the residual pathway
        self.dropout = Dropout(dropout) # adding drop out to prevent overfitting

    def forward(self, x):
        out = cat([h(x) for h in self.heads], dim = - 1)
        out = self.dropout(self.proj(out))
        return out
from .checkpointed import CheckPointed
from .attention import MultiSelfAttentionHead
from .feedforward import FeedForward
from torch.nn import Module, LayerNorm

class SelfAttentionBlock(Module):
    def __init__(self, number_of_embeddings: int, number_of_heads: int, block_size: int, dropout_rate: float, device: str = 'cpu'):
        super().__init__()
        head_size = number_of_embeddings // number_of_heads # we want the concat to equal what one head would've looked like so we need to divide it up
        self.self_attention = CheckPointed(
            LayerNorm(number_of_embeddings),
            MultiSelfAttentionHead(number_of_embeddings, head_size, block_size, number_of_heads, dropout_rate, device = device)
        )
        self.ffwd = CheckPointed(
            LayerNorm(number_of_embeddings),
            FeedForward(number_of_embeddings)
        )

    def forward(self, x):
        # we want to add x to itself to apply some residual pathway which will make the blocks "slowly come online"
        out = self.self_attention(x) + x # apply self attention (B, T, C)
        out = self.ffwd(out) + x # (B, T, C)
        return out
from util.checkpointed import CheckPointed
from util.attention import MultiSelfAttentionHead
from util.feedforward import FeedForward
from torch.nn import Module, LayerNorm

class SelfAttentionBlock(Module):
    def __init__(self, number_of_embeddings: int, number_of_heads: int, block_size: int, dropout_rate: float):
        super().__init__()
        head_size = number_of_embeddings // number_of_heads # we want the concat to equal what one head would've looked like so we need to divide it up
        self.self_attention = CheckPointed(
            LayerNorm(number_of_embeddings),
            MultiSelfAttentionHead(number_of_embeddings, head_size, block_size, number_of_heads, dropout_rate)
        )
        self.ffwd = CheckPointed(
            LayerNorm(number_of_embeddings),
            FeedForward(number_of_embeddings)
        )

    def forward(self, x):
        # we want to add x to itself to apply some residual pathway which will make the blocks "slowly come online"
        x += self.self_attention(x) # apply self attention (B, T, C)
        x += self.ffwd(x) # (B, T, C)
        return x
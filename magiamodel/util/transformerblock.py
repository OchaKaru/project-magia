from util.attention import MultiSelfAttentionHead
from util.feedforward import FeedForward
from torch.nn import Module, LayerNorm

class SelfAttentionBlock(Module):
    def __init__(self, n_embed, n_head):
        super().__init__()
        head_size = n_embed // n_head # we want the concat to equal what one head would've looked like so we need to divide it up
        self.ln1 = LayerNorm(n_embed)
        self.self_attention = MultiSelfAttentionHead(n_head, head_size) # self attention head list
        self.ln2 = LayerNorm(n_embed)
        self.ffwd = FeedForward(n_embed)

    def forward(self, x):
        # we want to add x to itself to apply some residual pathway which will make the blocks "slowly come online"
        x = x + self.self_attention(self.ln1(x)) # apply self attention (B, T, C)
        x = x + self.ffwd(self.ln2(x)) # (B, T, C)
        return x
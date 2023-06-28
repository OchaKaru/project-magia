from utils.checkpointed import CheckPointed
from utils.transformerblock import SelfAttentionBlock
from torch import autocast, cat, multinomial
from torch.nn import Module, Embedding, LayerNorm, Linear
from torch.nn.functional import softmax, cross_entropy

from io import BytesIO
from os.path import exists

class GPTModel(Module):
    def __init__(self, vocab_size: int, number_of_embeddings: int = 128, block_size: int = 64, number_of_heads: int = 3, number_of_layers: int = 3, dropout_rate: float = 0.4):
        super().__init__()
        # each token directly reads off the logits for the next token from a lookup table
        self.token_embedding_table = Embedding(vocab_size, number_of_embeddings)
        self.position_embedding_table = Embedding(block_size, number_of_embeddings) # positional embedding to add the spatial feature to attention
        self.blocks = CheckPointed(*[SelfAttentionBlock(number_of_embeddings, number_of_heads, block_size, dropout_rate) for _ in range(number_of_layers)]) # asterisk here unpacks the list
        self.lnf = LayerNorm(number_of_embeddings) # final layer norm
        self.lang_model_head = Linear(number_of_embeddings, vocab_size) # language model head
        
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets = None, device = 'cpu'):
        B, T = idx.shape
        # idx and targets are both (B, T) tensor of integers
        token_embeddings = self.token_embedding_table(idx) # (B, T, C)
        position_embeddings = self.position_embedding_table(torch.arange(T, device = device)) # (T, C)
        x = token_embeddings + position_embeddings # (B, T, C)
        x = self.lnf(self.blocks(x)) # apply alternating self attention and computation (B, T, C) then layer norm
        logits = self.lang_model_head(x) # (B, T, vocab_size)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B * T, C)
            targets = targets.view(B * T) # could also use -1 because pytorch will guess

            loss = cross_entropy(logits, targets)

        return logits, loss

    def generate(self, idx, max_new_tokens):
        # idx is (B, T) array in the current context
        for _ in range(max_new_tokens):
            # crop context
            idx_cond = idx[:, -block_size:]
            # predictions
            logits, _ = self(idx_cond)
            # focus in on last step
            logits = logits[:,-1,:] # becomes (B, C)
            # apply soft max to get probabilities
            with autocast(device_type = device, dtype = torch.float32):
                probs = softmax(logits, dim = -1) # (B, C)
            # sample
            idx_next = multinomial(probs, num_samples = 1) # (B, 1)
            # append sampled index to the sequence
            idx = cat((idx, idx_next), dim = 1) # (B, T + 1)
        return idx
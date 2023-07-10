import json
import tiktoken

from magiamodel.magiagen import GPTModel
from modeltraining.train import ModelTrainer

file = open("./sessions/modelinfo/hyperparams.json", 'r')
hyperparams = json.loads(file.read())
file.close()

device = 'cuda'

if hyperparams['vocab_size'] == 0:
    file = open("./sessions/modelinfo/hyperparams.json", 'w')
    hyperparams['vocab_size'] = tiktoken.encoding_for_model("gpt-4").n_vocab
    json.dump(hyperparams, file)
    file.close()

magiagpt = GPTModel(
    hyperparams['vocab_size'],
    number_of_embeddings = hyperparams['n_embed'],
    block_size = hyperparams['block_size'],
    number_of_heads = hyperparams['n_heads'],
    number_of_layers = hyperparams['n_layers'],
    dropout_rate = hyperparams['dropout_rate'],
    device = device
).cuda()

trainer = ModelTrainer(magiagpt, device = device)
trainer.train()
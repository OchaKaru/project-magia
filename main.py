from .magiamodel.magiagen import GPTModel
from .modeltraining.train import ModelTrainer

with open("./sessions/modelinfo/hyperparams.json", 'rw') as file:
    hyperparams = json.loads(file.read())        

    if hyperparams['vocab_size'] == 0:
        hyperparams['vocab_size'] = tiktoken.encoding_for_model("gpt-3").n_vocab
        file.write(json.dump(hyperparams))
    file.close()

    magiagpt = GPTModel(
        self.hyperparams['vocab_size'],
        number_of_embeddings = self.hyperparams['n_embed'],
        block_size = self.hyperparams['block_size'],
        number_of_heads = self.hyperparams['n_heads'],
        number_of_layers = self.hyperparams['n_layers'],
        dropout_rate = self.hyperparams['dropout_rate']
    ).cuda()

trainer = ModelTrainer(magiagpt)
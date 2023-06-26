from magiamodel.magiagen import GPTModel
from bitsandbytes import optim
import tiktoken
import json

from torch import autocast, no_grad, zeros
from torch.cuda.amp import GradScaler

class ModelTrainer():
    def __init__(self, model, param_file: str = '../sessions/hyperparams.json', device: str = 'cuda', attempt_load = True):        
        self.param_file = param_file
        with open(self.param_file, 'r') as file:
            self.hyperparams = json.loads(file.read())        
            self.encoder = tiktoken.encoding_for_model("gpt-4")
            self.hyperparams['vocab_size'] = enc.n_vocab
            file.close()
        
        self.device = device
            
        self.model_to_train = model
        if attempt_load:
            self._load_model()
            
        self.optimizer = optim.AdamW8bit(magia.parameters(), lr = self.hyperparams['learning_rate'])
        self.scaler = GradScaler()
        
        self._download_data()
            
    def _save_model(self):
        torch.save(self.model.state_dict(), self.hyperparams['model_file'])
        file_metadata = {'name': self.hyperparams['model_file'], 'parents': self.hyperparams['parent_drive_ids']}
                
        new_drive_id = self.service_client.resumable_upload(self.hyperparams['model_file'], metadata = file_metadata, mimetype = 'text/plain')
        
        if self.hyperparams['model_drive_id'] is not None:
            self.service_client.delete(self.hyperparams['model_drive_id'])
        
        self.hyperparams['model_drive_id'] = new_drive_id
        with open(self.param_file, 'w') as file:
            file.write(json.dump(self.hyperparams))
            file.close()
    
    def _load_model(self):
        if exists(self.hyperparams['model_file']):
            self.model_to_train.load_state_dict(torch.load(self.hyperparams['model_file']))
        elif self.hyperparams['model_drive_id'] is not None:
            model_file = self.service_client.download(self.hyperparams['model_drive_id'])
            self.model_to_train.load_state_dict(torch.load(BytesIO(model_file.getvalue())))
            
    def _download_data():
        
    
    def _training_step():
        data, targets = self._get_batch('train')

        with autocast(device_type = self.device, dtype = torch.float16):
            _, train_loss = magia(data, targets)
            train_loss /= accumulation_step

        self.scaler.scale(train_loss).backward()
        train_loss_output = train_loss.detach()
        
    def _accumulation_step():
        self.scaler.step(self.optimizer)
        self.optimizer.zero_grad(set_to_none = True)
        self.scaler.update()
    
    @no_grad()
    def _evaluate_model():
        self.model.eval()
        losses = zeros(self.hyperparams['eval_iterations'])
        out = {'train': 0, 'eval': 0}
        
        with autocast(device_type = self.device, dtype = torch.float16):
            for split in ['train', 'eval']:
                for step in range(self.hyperparams['eval_iterations']:
                    data, targets = self._get_batch(split)
                    _, loss = model(data, targets)
                    losses[step] = loss.detach().item()
                out[split] = losses.mean()

        self.model.train()
        return out
            
        
    def train(self):
        accumulation_step = int(self.hyperparams['batch_accumulation'] / self.hyperparams['batch_size'])

        # magia = GPTModel(
        #     self.hyperparams['vocab_size'],
        #     number_of_embeddings = self.hyperparams['n_embed'],
        #     block_size = self.hyperparams['block_size'],
        #     number_of_heads = self.hyperparams['n_heads'],
        #     number_of_layers = self.hyperparams['n_layers'],
        #     dropout_rate = self.hyperparams['dropout_rate']
        # ).cuda()

        step_count = self.hyperparams['max_iterations'] * self.hyperparams['accumulation_step']
        for step in range(step_count):
            self._training_step()

            if step % accumulation_step == accumulation_step - 1 or step == step_count - 1:
                self._accumulation_step()

            if step % self.hyperparam['eval_interval'] == 0 or step == step_count - 1:
                print(self._evaluate_model(), self._save_model())
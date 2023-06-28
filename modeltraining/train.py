from .datacollector import DataCollector
from bitsandbytes import optim
import tiktoken
import json

from torch import autocast, no_grad, zeros, tensor, stack, randint
from torch.cuda.amp import GradScaler

class ModelTrainer():
    def __init__(self, model, training_param_file: str = '../sessions/modelinfo/trainparams.json', data_loc_file: str = "../sessions/dataloc.json", device: str = 'cuda', attempt_load = True):        
        self.param_file = training_param_file

        self.data_storage_loc = data_loc_file
        with open(self.param_file, 'r') as file:
            self.data_loc = json.loads(file.read())
            file.close()
        
        self.device = device
            
        self.model_to_train = model
        if attempt_load:
            self._load_model()
            
        self.encoder = tiktoken.encoding_for_model("gpt-3")            
        self.optimizer = optim.AdamW8bit(magia.parameters(), lr = self.hyperparams['learning_rate'])
        self.scaler = GradScaler()
        
        self.train_data = None
        self.eval_data = None
            
    def _save_model(self):
        torch.save(self.model.state_dict(), self.data_loc['model_file'])
        file_metadata = {'name': self.data_loc['model_file'], 'parents': self.data_loc['parent_drive_ids']}
                
        new_drive_id = self.service_client.resumable_upload(self.data_loc['model_file'], metadata = file_metadata, mimetype = 'text/plain')
        
        if self.data_loc['model_drive_id'] != '':
            self.service_client.delete(self.data_loc['model_drive_id'])
        
        self.data_loc['model_drive_id'] = new_drive_id
        with open(self.data_loc_file, 'w') as file:
            file.write(json.dump(self.data_loc))
            file.close()
    
    def _load_model(self):
        if exists(self.data_loc['model_file']):
            self.model_to_train.load_state_dict(torch.load(self.data_loc['model_file']))
        elif self.data_loc['model_drive_id'] != '':
            model_file = self.service_client.download(self.data_loc['model_drive_id'])
            self.model_to_train.load_state_dict(torch.load(BytesIO(model_file.getvalue())))
            
    def _download_data(self, corpus_type: str):
        downloader = DataCollector()
        with open("../sessions/dataloc.json", "rw", encode = 'utf-8') as file:
            data_loc = json.loads(file.read())
            data = tensor(self.encoder.encode(downloader.download_data(data_loc['corpus_drive_ids'][corpus_type]).decode('UTF-8')))
            n = int(.85 * len(data))
            
            self.train_data = data[:n]
            self.eval_data = data[n:]
            
            data_loc['last_corpus_type'] = corpus_type
            file.write(json.dump(data_loc))
            
    def _get_batch(self, data_set)
        #generate small bacth of data input x and target y
        data = self.train_data if split == 'train' else self.eval_data
        ix = randint(len(data) - block_size, (batch_size,)) # generates an array of random numbers with the shape (batch_size,) and max range len(data) - block_size

        x = stack([data[i : i + block_size] for i in ix])
        y = stack([data[i + 1 : i + block_size + 1] for i in ix])

        x, y = x.to(device), y.to(device) # sending to the current device
        return x, y
    
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
        step_count = self.hyperparams['max_iterations'] * self.hyperparams['accumulation_step']

        for split in ['anime', 'manga', 'games']:
            self._download_data(split)
            for step in range(step_count):
                self._training_step()

                if step % accumulation_step == accumulation_step - 1 or step == step_count - 1:
                    self._accumulation_step()

                if step % self.hyperparam['eval_interval'] == 0 or step == step_count - 1:
                    print(self._evaluate_model(), self._save_model())
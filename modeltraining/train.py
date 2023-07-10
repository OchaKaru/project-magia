from .datacollector import DataCollector
from .api.googledrive.driveapi import DriveAPI
from .util.progressbar import progress_bar
from bitsandbytes import optim
import tiktoken
import json

from torch import autocast, no_grad, zeros, tensor, stack, randint, float16, save, load
from torch.cuda.amp import GradScaler

from os.path import exists

class ModelTrainer():
    def __init__(self, model, training_param_file: str = './sessions/modelinfo/trainparams.json', data_loc_file: str = "./sessions/modelinfo/dataloc.json", device: str = 'cpu', attempt_load: bool = True, drive_cred_file: str = './sessions/google-drive-cred.json'):        
        self.param_file = training_param_file
        with open(self.param_file, 'r') as file:
            self.training_params = json.load(file)
            file.close()

        self.data_storage_loc = data_loc_file
        with open(self.data_storage_loc, 'r') as file:
            self.data_loc = json.load(file)
            file.close()

        self.device = device

        self.encoder = tiktoken.encoding_for_model("gpt-4")            
        self.optimizer = optim.AdamW8bit(self.model_to_train.parameters(), lr = self.training_params['learning_rate'])
        self.scaler = GradScaler()
        self.service_client = DriveAPI(drive_cred_file)

        self.train_data = None
        self.eval_data = None
        self.accumulation_step = -1
        
        self.model_to_train = model
        if attempt_load:
            self._load_model()

    def _save_model(self):
        save(self.model_to_train.state_dict(), self.data_loc['model_file'])
        file_metadata = {'name': self.data_loc['model_file_name'], 'parents': self.data_loc['model_parent_ids']}

        new_drive_id = self.service_client.resumable_upload(self.data_loc['model_file'], metadata = file_metadata, mimetype = 'text/plain')

        if self.data_loc['model_drive_id'] != '':
            self.service_client.delete(self.data_loc['model_drive_id'])

        self.data_loc['model_drive_id'] = new_drive_id
        file = open(self.data_storage_loc, 'w')
        json.dump(self.data_loc, file)
        file.close()
        
        return new_drive_id

    def _load_model(self):
        if exists(self.data_loc['model_file']):
            self.model_to_train.load_state_dict(load(self.data_loc['model_file']))
        elif self.data_loc['model_drive_id'] != '':
            model_file = self.service_client.download(self.data_loc['model_drive_id'])
            self.model_to_train.load_state_dict(load(BytesIO(model_file.getvalue())))

    def _download_data(self, corpus_type: str):
        downloader = DataCollector()
        file = open("./sessions/modelinfo/dataloc.json", "r")
        data_loc = json.load(file)
        file.close()
        
        data = tensor(self.encoder.encode(downloader.download_data(data_loc['corpus_drive_ids'][corpus_type]).decode('UTF-8')))
        n = int(.85 * len(data))
            
        self.train_data = data[:n]
        self.eval_data = data[n:]
        
        file = open("./sessions/modelinfo/dataloc.json", "w")
        data_loc['last_corpus_type'] = corpus_type
        self.data_loc['progress_made'] = 0
        json.dump(data_loc, file)
        file.close()
        
    def _get_batch(self, data_set):
        #generate small bacth of data input x and target y
        data = self.train_data if data_set == 'train' else self.eval_data
        ix = randint(len(data) - self.training_params['block_size'], (self.training_params['batch_size'],)) # generates an array of random numbers with the shape (batch_size,) and max range len(data) - block_size

        x = stack([data[i : i +  self.training_params['block_size']] for i in ix])
        y = stack([data[i + 1 : i +  self.training_params['block_size'] + 1] for i in ix])

        x, y = x.to(self.device), y.to(self.device) # sending to the current device
        return x, y

    def _training_step(self):
        data, targets = self._get_batch('train')

        with autocast(device_type = self.device, dtype = float16):
            _, train_loss = self.model_to_train(data, targets)
            train_loss /= self.accumulation_step

        self.scaler.scale(train_loss).backward()
        train_loss_output = train_loss.detach()

    def _accumulation_step(self):
        self.scaler.step(self.optimizer)
        self.optimizer.zero_grad(set_to_none = True)
        self.scaler.update()

    @no_grad()
    def _evaluate_model(self):
        self.model_to_train.eval()
        losses = zeros(self.training_params['eval_iterations'])
        out = {'train': 0, 'eval': 0}
        
        with autocast(device_type = self.device, dtype = float16):
            for split in ['train', 'eval']:
                for step in range(self.training_params['eval_iterations']):
                    data, targets = self._get_batch(split)
                    _, loss = self.model_to_train(data, targets)
                    losses[step] = loss.detach().item()
                out[split] = losses.mean()

        self.model_to_train.train()
        return out

    def train(self):
        self.accumulation_step = int(self.training_params['batch_accumulation'] / self.training_params['batch_size'])

        for split in ['anime', 'manga', 'games']:
            if split != self.data_loc['last_corpus_type']:
                continue
            self._download_data(split)
            step_count = self.training_params['max_iterations'] * self.accumulation_step * (1 - self.data_loc['progress_made'])

            for step in range(step_count):
                if step % self.training_params['eval_interval'] == 0 or step == step_count - 1:
                    self.data_loc['progress_made'] = step / step_count
                    losses = self._evaluate_model()
                    print(f"For {split} data, step {step}:")
                    print(f"\tModel loss -> train: {losses['train']}, eval: {losses['eval']}")
                    drive_id = self._save_model()
                    print(f"\tModel sucessfully saved @ {drive_id}...")
                    progress_bar("Model Training Iterations", step / step_count)
                    print("\033[4A")
                
                self._training_step()

                if step % self.accumulation_step == self.accumulation_step - 1 or step == step_count - 1:
                    self._accumulation_step()
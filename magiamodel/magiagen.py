import torch
from torch import autocast
import torch.nn as nn
from torch.nn.functional import softmax, cross_entropy
from torch.utils.checkpoint import checkpoint

import bitsandbytes as bnb
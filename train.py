from torch.utils.data import Dataset, DataLoader
import torch
from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import random
from torch.utils.data import DataLoader
from torch.nn import CrossEntropyLoss
from transformers import get_linear_schedule_with_warmup
from torch import nn, optim
from tqdm import tqdm, trange
from torch.nn.utils.rnn import pad_sequence
import numpy as np
from preprocess import GPT2Dataset

load = False
loadepoch = 0
# basepath = '/users/zhoffman/Video2Gif'
basepath = '.'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

if __name__ == "__main__":
    print("device", device)
    print("loading gpt2 tokenizer")
    gpt2Tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')

    print("loading dataset")
    train_dataset = GPT2Dataset('./training.tsv', gpt2Tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    
    print("loading modle")
    vocab_size = len(gpt2Tokenizer) + len(train_dataset.vid_vocab)
    model = GPT2LMHeadModel.from_pretrained('gpt2', return_dict=True)
    model.resize_token_embeddings(vocab_size)

    if load:
        epoch = 0
        model.load_state_dict(torch.load(basepath + '/checkpoints/{}.cpt'.format(loadepoch)))
    
    model = model.to(device)
    print("testing training")
    optimizer = optim.Adam(model.parameters(), 0.0005)
    model = model.train()
    loss_fn = CrossEntropyLoss(ignore_index=-100)
    epochs = 101
    for epoch in range(epochs):
        losses = []
        for batch in tqdm(train_loader):
            input_ids = batch["input_ids"].to(device)
            mask = batch["mask"].to(device)
            labels = batch["labels"].to(device)

            out = model(
                input_ids=input_ids,
                attention_mask=mask,
                labels=labels,
            )
            logits = out.logits
            optimizer.zero_grad()
            loss = loss_fn(logits.permute(0, 2, 1), labels)
            loss.backward()
            optimizer.step()

            losses.append(torch.exp(loss).item())
        print("epoch", epoch, "perplexity:", np.mean(losses))

        if epoch % 5 == 0:
            torch.save(model.state_dict(), basepath + '/checkpoints/{}.cpt'.format(epoch))
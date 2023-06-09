import os
import pickle
import torch
import wandb
import pandas as pd
from args import parse_args
from sequential import trainer
from sequential.dataloader import Preprocess, add_features, post_process
from sequential.utils import setSeeds


def main(args):
    wandb.login()

    setSeeds(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    args.device = device    

    args = add_features(args)

    preprocess = Preprocess(args)
    preprocess.load_train_data(args.file_name)
    train_data = preprocess.get_train_data() 
        
    train_data, valid_data = preprocess.split_data(train_data,ratio=0.9) 

    wandb.init(project="sequential", config=vars(args))
    trainer.run(args, train_data, valid_data)


if __name__ == "__main__":
    args = parse_args(mode="train")
    os.makedirs(args.model_dir, exist_ok=True)
    main(args)

import os

import pandas as pd
import torch


def prepare_dataset(device, basepath, verbose=True, logger=None):
    data = load_data(basepath)
    train_data, valid_data, test_data = separate_data(data, basepath)
    id2index = indexing_data(data)
    train_data_proc = process_data(train_data, id2index, device)
    valid_data_proc = process_data(valid_data, id2index, device)
    test_data_proc = process_data(test_data, id2index, device)

    if verbose:
        print_data_stat(train_data, "Train", logger=logger)
        print_data_stat(valid_data, "Valid", logger=logger)
        print_data_stat(test_data, "Test", logger=logger)

    return train_data_proc, valid_data_proc, test_data_proc, len(id2index)


def load_data(basepath):
    path1 = os.path.join('/opt/ml/level2-sequential-level2-recsys-08/data_pkl/train_data.pkl')
    path2 = os.path.join('/opt/ml/level2-sequential-level2-recsys-08/data_pkl/test_data.pkl')
    data1 = pd.read_pickle(path1)
    data2 = pd.read_pickle(path2)

    data = pd.concat([data1, data2])
    data.drop_duplicates(
        subset=["userID", "assessmentItemID"], keep="last", inplace=True
    )

    return data


def separate_data(data, basepath):
    path = os.path.join(basepath, 'lcn_valid_data.csv') # subset of training set
    valid_data = pd.read_csv(path)

    train_data = data[(data.answerCode >= 0)]
    train_data = pd.concat([train_data, valid_data]).drop_duplicates(keep=False)
    test_data = data[data.answerCode == -1]

    return train_data, valid_data, test_data


def indexing_data(data):
    userid, itemid = (
        sorted(list(set(data.userID))),
        sorted(list(set(data.assessmentItemID))),
    )
    n_user, n_item = len(userid), len(itemid)

    userid_2_index = {v: i for i, v in enumerate(userid)}
    itemid_2_index = {v: i + n_user for i, v in enumerate(itemid)}
    id_2_index = dict(userid_2_index, **itemid_2_index)

    return id_2_index


def process_data(data, id_2_index, device):
    edge, label = [], []
    for user, item, acode in zip(data.userID, data.assessmentItemID, data.answerCode):
        uid, iid = id_2_index[user], id_2_index[item]
        edge.append([uid, iid])
        label.append(acode)

    edge = torch.LongTensor(edge).T
    label = torch.LongTensor(label)

    return dict(edge=edge.to(device), label=label.to(device))


def print_data_stat(data, name, logger):
    userid, itemid = list(set(data.userID)), list(set(data.assessmentItemID))
    n_user, n_item = len(userid), len(itemid)

    logger.info(f"{name} Dataset Info")
    logger.info(f" * Num. Users    : {n_user}")
    logger.info(f" * Max. UserID   : {max(userid)}")
    logger.info(f" * Num. Items    : {n_item}")
    logger.info(f" * Num. Records  : {len(data)}")

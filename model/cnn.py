import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

import re
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(13, 1, 1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(1, 2, 2)
        self.fc1 = nn.Linear( 2, 10)
        self.fc4 = nn.Linear(10, 10)

    def forward(self, x):
        x = self.pool(self.conv1(x))
        x = self.pool(self.conv2(x))
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = self.fc4(x)
        return x


class ChessDataset(Dataset):
    def __init__(self, data_frame):
        self.fens = torch.from_numpy(np.array([*map(fen_to_bit_vector, data_frame["FEN"])], dtype=np.float32))
        self.evals = torch.Tensor([[x] for x in data_frame["Evaluation"]])
        self._len = len(self.evals)
        
    def __len__(self):
        return self._len
    
    def __getitem__(self, index):
        return self.fens[index], self.evals[index]

def eval_to_int(evaluation):
    try:
        res = int(evaluation)
    except ValueError:
        res = 10000 if evaluation[1] == '+' else -10000
    return res / 100

def fen_to_bit_vector(fen):
   
    
    parts = re.split(" ", fen)
    piece_placement = re.split("/", parts[0])
    active_color = parts[1]
    castling_rights = parts[2]
    en_passant = parts[3]
    halfmove_clock = int(parts[4])
    fullmove_clock = int(parts[5])

    bit_vector = np.zeros((13, 8, 8), dtype=np.uint8)
    
    piece_to_layer = {
        'R': 1,
        'N': 2,
        'B': 3,
        'Q': 4,
        'K': 5,
        'P': 6,
        'p': 7,
        'k': 8,
        'q': 9,
        'b': 10,
        'n': 11,
        'r': 12
    }
    
    castling = {
        'K': (7,7),
        'Q': (7,0),
        'k': (0,7),
        'q': (0,0),
    }

    for r, row in enumerate(piece_placement):
        c = 0
        for piece in row:
            if piece in piece_to_layer:
                bit_vector[piece_to_layer[piece], r, c] = 1
                c += 1
            else:
                c += int(piece)
    
    if en_passant != '-':
        bit_vector[0, ord(en_passant[0]) - ord('a'), int(en_passant[1]) - 1] = 1
    
    if castling_rights != '-':
        for char in castling_rights:
            bit_vector[0, castling[char][0], castling[char][1]] = 1
    
    if active_color == 'w':
        bit_vector[0, 7, 4] = 1
    else:
        bit_vector[0, 0, 4] = 1

    if halfmove_clock > 0:
        c = 7
        while halfmove_clock > 0:
            bit_vector[0, 3, c] = halfmove_clock%2
            halfmove_clock = halfmove_clock // 2
            c -= 1
            if c < 0:
                break

    if fullmove_clock > 0:
        c = 7
        while fullmove_clock > 0:
            bit_vector[0, 4, c] = fullmove_clock%2
            fullmove_clock = fullmove_clock // 2
            c -= 1
            if c < 0:
                break

    return bit_vector

def AdamW_main():
    MAX_DATA = 100000
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device {}".format(device))

    print("Preparing Training Data...")
    train_data = pd.read_csv("./data/chessData.csv")
    # train_data = train_data[:MAX_DATA]
    train_data["Evaluation"] = train_data["Evaluation"].map(eval_to_int)
    trainset = ChessDataset(train_data)
    
    print("Preparing Test Data...")
    test_data = pd.read_csv("./data/tactic_evals.csv")
    # test_data = test_data[:MAX_DATA]
    test_data["Evaluation"] = test_data["Evaluation"].map(eval_to_int)
    testset = ChessDataset(test_data)

    batch_size = 10

    print("Converting to pytorch Dataset...")

    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=2)

    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)


    net = Net().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(net.parameters())


    for epoch in range(10):  # loop over the dataset multiple times

        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            inputs = inputs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()

            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:    # print every 2000 mini-batches
                # denominator for loss should represent the number of positions evaluated 
                # independent of the batch size

                torch.save('model.pt')
                print('[%d, %5d] loss: %.3f' % (epoch + 1, i + 1, running_loss / (2000*len(labels))))
                running_loss = 0.0

    print('Finished Training')

    PATH = './chess.pth'
    torch.save(net.state_dict(), PATH)

    print('Evaluating model')

    count = 0
    total_loss = 0
    # since we're not training, we don't need to calculate the gradients for our outputs
    with torch.no_grad():
        for data in testloader:
            inputs, labels = data
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            #print("Correct eval: {}, Predicted eval: {}, loss: {}".format(labels, outputs, loss))
            
            # count should represent the number of positions evaluated 
            # independent of the batch size
            count += len(labels)
            total_loss += loss
            if count % 10000 == 0:
                print('Average error of the model on the {} tactics positions is {}'.format(count, loss/count))
    #print('Average error of the model on the {} tactics positions is {}'.format(count, loss/count))



AdamW_main()

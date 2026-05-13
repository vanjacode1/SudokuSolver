from torch import nn

class DigitNet(nn.Module):
    """
    Small CNN for classifying Sudoku digits 1..9 from 28x28 grayscale image crops.
    """
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64 , kernel_size=3, padding=1)
        #self.conv3 = nn.Conv2d(64, 128, kernel_size=3)

        self.pooling = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()

        self.flatten = nn.Flatten()
        self.linear = nn.Linear((64*7*7), 64)

        self.dropout = nn.Dropout(0.3)

        self.output = nn.Linear(64, 9)

    def forward(self, x):
        x = self.conv1(x) # (32, 28, 28)
        x = self.pooling(x) # (32, 14, 14)
        x = self.relu(x)

        x = self.conv2(x) # (64, 14, 14)
        x = self.pooling(x) # (64, 7, 7)
        x = self.relu(x)

        x = self.flatten(x) # (64*7*7)
        x = self.linear(x) # (128)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.output(x) # (9)
        return x
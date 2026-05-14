from torch import nn

class DigitNet(nn.Module):
    """
    Small CNN for classifying Sudoku digits 1..9 from 28x28 grayscale images.
    """
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3)

        self.pooling = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()
        self.flatten = nn.Flatten()

        self.fc1 = nn.Linear(128 * 2 * 2, 128)
        self.fc2 = nn.Linear(128, 20)

        self.dropout = nn.Dropout(0.5)

        self.output = nn.Linear(20, 9)

    def forward(self, x):
        x = self.conv1(x) # [B, 32, 28, 28]
        x = self.relu(x)
        x = self.pooling(x) # [B, 32, 14, 14]

        x = self.conv2(x) # [B, 64, 14, 14]
        x = self.relu(x)
        x = self.pooling(x) # [B, 64, 7, 7]

        x = self.conv3(x) # [B, 128, 5, 5]
        x = self.relu(x)
        x = self.pooling(x) # [B, 128, 2, 2]

        x = self.flatten(x) # [B, 128 * 2 * 2]

        x = self.fc1(x) # [B, 128]
        x = self.relu(x)

        x = self.fc2(x) # [B, 20]
        x = self.relu(x)

        x = self.dropout(x)

        x = self.output(x) # [B, 9]

        return x
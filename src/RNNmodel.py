import torch
import torch.nn as nn

class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size

        self.input_2_hidden = nn.Linear(input_size + hidden_size, hidden_size)
        self.input_2_output = nn.Linear(input_size + hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        # change to lstm or gru
        combined = torch.cat((input.view(1,-1), hidden), 1)
        hidden = self.input_2_hidden(combined)
        output = self.input_2_output(combined)
        output = self.softmax(output)
        output = torch.sigmoid(output)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, self.hidden_size)
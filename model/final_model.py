import torch
from torchvision import models

class ImageClassifier(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = models.efficientnet_b1(pretrained=True)
        self.encoder.classifier = torch.nn.Sequential(
            torch.nn.Linear(1280, 2048),
            torch.nn.SiLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(2048, 400)
        )

    def forward(self, x):
        return self.encoder(x)

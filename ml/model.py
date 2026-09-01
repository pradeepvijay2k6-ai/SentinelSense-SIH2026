"""
PyTorch Deep ConvNet (SentinelSleepNet) for AASM 5-Stage Sleep Classification.
Processes 4-channel Continuous Wavelet / Spectrogram scalograms [B, 4, 32, 64].
SIH 2026 Problem Statement 26186.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        residual = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        out = self.relu(out)
        return out

class SentinelSleepNet(nn.Module):
    """
    Multi-channel ResNet-style Deep ConvNet for sleep stage classification.
    Inputs: [Batch, 4 channels (ECG, EMG, EOG, Motion), 32 freqs, 64 time_steps]
    Outputs: [Batch, 5 classes (Wake, N1, N2, N3, REM)]
    """
    def __init__(self, in_channels=4, num_classes=5):
        super().__init__()
        # Initial stem
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2) # Shape: [B, 32, 16, 32]
        )
        
        # ResNet stages
        self.stage1 = nn.Sequential(
            ResidualBlock(32, 32),
            ResidualBlock(32, 32)
        )
        
        self.stage2 = nn.Sequential(
            ResidualBlock(32, 64, stride=2), # Shape: [B, 64, 8, 16]
            ResidualBlock(64, 64)
        )
        
        self.stage3 = nn.Sequential(
            ResidualBlock(64, 128, stride=2), # Shape: [B, 128, 4, 8]
            ResidualBlock(128, 128)
        )
        
        # Adaptive pooling + Classifier
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        # x shape: [B, C, F, T]
        x = self.stem(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        logits = self.fc(x)
        return logits

def get_model(checkpoint_path=None, device="cpu"):
    model = SentinelSleepNet(in_channels=4, num_classes=5)
    if checkpoint_path:
        import os
        if os.path.exists(checkpoint_path):
            state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
            model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model

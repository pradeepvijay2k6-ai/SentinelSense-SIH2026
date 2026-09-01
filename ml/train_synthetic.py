"""
Training and Checkpoint Generator for SentinelSleepNet.
SIH 2026 Problem Statement 26186.

Generates training epochs across sleep stages (Wake, N1, N2, N3, REM),
computes 4-channel CWT/spectrogram scalograms, trains the PyTorch model,
and exports ml/checkpoint.pt.
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Add workspace to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sample_data.generate_synthetic import (
    generate_ecg_epoch, generate_emg_epoch, generate_eog_epoch, generate_motion_epoch
)
from ml.cwt_utils import extract_multimodal_scalogram_tensor, STAGE_TO_IDX
from ml.model import SentinelSleepNet

class SleepEpochDataset(Dataset):
    def __init__(self, num_samples_per_stage=120, fs=100):
        self.samples = []
        self.labels = []
        
        stages = ["W", "N1", "N2", "N3", "REM"]
        print(f"Generating {num_samples_per_stage * len(stages)} synthetic epochs for training...")
        
        for stage in stages:
            stage_idx = STAGE_TO_IDX[stage]
            for i in range(num_samples_per_stage):
                stress = np.random.uniform(0.1, 0.9)
                hr = np.random.randint(50, 95)
                hrv = np.random.randint(18, 75)
                
                ecg = generate_ecg_epoch(30, fs, hr_bpm=hr, hrv_std_ms=hrv, stress_factor=stress)
                emg = generate_emg_epoch(30, fs, stage=stage, stress_factor=stress)
                eog = generate_eog_epoch(30, fs, stage=stage)
                _, _, _, motion = generate_motion_epoch(30, fs, stage=stage, is_restless=(np.random.rand() < 0.3))
                
                # Add data augmentation noise
                ecg += np.random.normal(0, 0.02, len(ecg))
                emg += np.random.normal(0, 1.5, len(emg))
                eog += np.random.normal(0, 2.0, len(eog))
                
                epoch_dict = {"ecg": ecg, "emg": emg, "eog": eog, "motion": motion}
                tensor_4ch = extract_multimodal_scalogram_tensor(epoch_dict, fs=fs)
                
                self.samples.append(tensor_4ch)
                self.labels.append(stage_idx)
                
        self.samples = np.array(self.samples, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return torch.tensor(self.samples[idx]), torch.tensor(self.labels[idx])

def train_and_save_model(output_path="ml/checkpoint.pt", epochs=12, batch_size=32):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    dataset = SleepEpochDataset(num_samples_per_stage=100, fs=100)
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    model = SentinelSleepNet(in_channels=4, num_classes=5).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * x.size(0)
            preds = torch.argmax(out, dim=1)
            correct += (preds == y).sum().item()
            total += x.size(0)
            
        scheduler.step()
        epoch_acc = (correct / total) * 100.0
        print(f"Epoch {epoch+1:02d}/{epochs} - Loss: {total_loss/total:.4f} - Accuracy: {epoch_acc:.2f}%")
        
    torch.save(model.state_dict(), output_path)
    print(f"Trained checkpoint saved successfully to {output_path}")

if __name__ == "__main__":
    train_and_save_model()

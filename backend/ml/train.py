import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import logging
from typing import Tuple

# Import your local models
from models.basic_unet import BasicUNetScout
from models.swin_unet import SwinUNetSniper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DummySARDataset(Dataset):
    """
    A synthesized dataset to validate the training pipeline locally 
    before mounting massive production SAR datasets.
    """
    def __init__(self, num_samples=32, img_size=512):
        self.num_samples = num_samples
        self.img_size = img_size

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx) -> Tuple[torch.Tensor, torch.Tensor]:
        # Generate fake 1-channel SAR chip
        image = torch.randn(1, self.img_size, self.img_size)
        # Generate fake 1-channel ground truth mask
        mask = torch.zeros(1, self.img_size, self.img_size)
        # Inject artificial anomaly (oil spill) in the mask
        mask[:, 200:300, 200:300] = 1.0 
        return image, mask

def train_model(model_name: str, epochs: int = 2, batch_size: int = 4):
    """
    Master training loop. Handles both Scout and Sniper architectures.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Initiating training for {model_name} on {device}...")

    # Select Architecture
    if model_name == "scout":
        model = BasicUNetScout(n_channels=1, n_classes=1).to(device)
    elif model_name == "sniper":
        model = SwinUNetSniper().to(device)
    else:
        raise ValueError("Invalid model name. Choose 'scout' or 'sniper'.")

    # Load Dataset & DataLoader
    dataset = DummySARDataset(num_samples=16) # Keeping it small for rapid testing
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Loss and Optimizer
    # BCEWithLogitsLoss is mathematically required for binary segmentation (Oil vs No Oil)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-5)

    model.train()
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        
        for batch_idx, (images, true_masks) in enumerate(dataloader):
            images = images.to(device)
            true_masks = true_masks.to(device)
            
            # Forward pass
            optimizer.zero_grad()
            logits = model(images)
            
            # Calculate Loss
            loss = criterion(logits, true_masks)
            
            # Backward pass & Optimizer step
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
        avg_loss = epoch_loss / len(dataloader)
        logging.info(f"Epoch [{epoch+1}/{epochs}] | Average Loss: {avg_loss:.4f}")

    # Save model weights
    save_dir = os.path.join(os.path.dirname(__file__), "weights")
    os.makedirs(save_dir, exist_ok=True)
    weight_path = os.path.join(save_dir, f"{model_name}_latest.pth")
    
    torch.save(model.state_dict(), weight_path)
    logging.info(f"Training complete. Weights saved to {weight_path}")

# --- Test Execution Block ---
if __name__ == "__main__":
    logging.info("--- Starting ML Pipeline Validation ---")
    
    # Train the Scout (Basic U-Net)
    train_model(model_name="scout", epochs=1, batch_size=4)
    
    # Train the Sniper (Swin-UNet)
    train_model(model_name="sniper", epochs=1, batch_size=4)
    
    logging.info("--- ML Pipeline Validation Complete ---")
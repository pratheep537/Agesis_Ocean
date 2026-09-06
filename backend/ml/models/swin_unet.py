import torch
import torch.nn as nn
import numpy as np
import cv2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class TransformerBlock(nn.Module):
    """
    Lightweight Transformer Block acting as our Swin representation.
    Extracts fractal texture variations to characterize oil weathering.
    """
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            nn.Linear(embed_dim * 4, embed_dim)
        )

    def forward(self, x):
        # x shape: [B, Seq_Len, Embed_Dim]
        attn_out, _ = self.attn(self.norm1(x), self.norm1(x), self.norm1(x))
        x = x + attn_out
        x = x + self.mlp(self.norm2(x))
        return x

class SwinUNetSniper(nn.Module):
    """
    Sniper Model triggered only on anomalous 10km chips.
    Input: 1-Channel SAR Image [B, 1, 512, 512]
    Output: 1-Channel High-Fidelity Polygon Mask [B, 1, 512, 512]
    """
    def __init__(self, img_size=512, patch_size=16, in_chans=1, embed_dim=64, num_heads=4):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        
        # Patch Embedding
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        
        # Transformer Encoder (Simulating Swin Blocks)
        self.transformer = TransformerBlock(embed_dim, num_heads)
        
        # Decoder (Upsampling back to 512x512 image space)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(embed_dim, 32, kernel_size=patch_size, stride=patch_size),
            nn.ReLU(),
            nn.Conv2d(32, 1, kernel_size=3, padding=1)
        )

    def forward(self, x):
        B, C, H, W = x.shape
        
        # Embed Patches
        x = self.proj(x)  # [B, Embed_Dim, H/Patch, W/Patch]
        
        # Flatten for Transformer
        x_flat = x.flatten(2).transpose(1, 2)  # [B, Num_Patches, Embed_Dim]
        
        # Apply Attention
        x_trans = self.transformer(x_flat)
        
        # Reshape for Decoder
        x_reshaped = x_trans.transpose(1, 2).view(B, -1, H // self.patch_size, W // self.patch_size)
        
        # Upsample to original mask size
        out = self.decoder(x_reshaped)
        return out

def extract_slick_centroid(logits_tensor: torch.Tensor):
    """
    The critical handoff function.
    Converts the AI segmentation mask into a geometric centroid for the physics SDE.
    """
    # Convert logits to binary mask (0 or 255)
    probs = torch.sigmoid(logits_tensor.squeeze())
    mask = (probs > 0.5).cpu().numpy().astype(np.uint8) * 255
    
    # Find oil slick boundaries (contours)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        logging.warning("Sniper executed, but no definitive slick geometry found.")
        return None, mask
        
    # Isolate the largest anomaly (main slick body)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Calculate spatial moments to find the exact geometric centroid
    M = cv2.moments(largest_contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0
        
    return (cX, cY), mask

# --- Test Execution Block ---
if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Target Compute Device: {device}")
    
    # Initialize Sniper
    sniper = SwinUNetSniper().to(device)
    
    # Simulate the exact 512x512 chip flagged by the Scout model
    dummy_input = torch.randn(1, 1, 512, 512).to(device)
    
    logging.info("Initiating Sniper sequence on flagged chip...")
    with torch.no_grad():
        mask_logits = sniper(dummy_input)
    
    logging.info(f"Sniper extraction complete. Mask shape: {mask_logits.shape}")
    
    # Force an artificial anomaly into the dummy tensor so OpenCV has something to find
    mask_logits[0, 0, 200:300, 200:300] = 10.0 
    
    centroid, binary_mask = extract_slick_centroid(mask_logits)
    logging.info(f"Geometry Extracted -> Slick Centroid (X,Y) Coordinates: {centroid}")
    logging.info("Handoff payload to Euler-Maruyama SDE is ready.")
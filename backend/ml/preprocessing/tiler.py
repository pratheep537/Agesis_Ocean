import os
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SARTiler:
    def __init__(self, tile_size=512):
        """
        Initializes the Tiling Engine.
        tile_size=512 is the standard input size for the Basic U-Net Scout.
        """
        self.tile_size = tile_size

    def tile_image(self, input_filepath: str, output_dir: str):
        """
        Slices a large SAR scene into manageable chips.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logging.info(f"Loading SAR scene: {input_filepath}")
        
        # Load grayscale (SAR is single-channel radar backscatter)
        img = cv2.imread(input_filepath, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise FileNotFoundError(f"Could not load image at {input_filepath}")

        h, w = img.shape
        logging.info(f"Scene dimensions: {w}x{h}. Tiling into {self.tile_size}x{self.tile_size} chips...")

        chip_count = 0

        # Iterate through the image in grid steps
        for y in range(0, h, self.tile_size):
            for x in range(0, w, self.tile_size):
                
                # Extract the chip
                chip = img[y:y+self.tile_size, x:x+self.tile_size]
                
                # Pad edges with black pixels (0) if the chip is smaller than tile_size
                if chip.shape[0] < self.tile_size or chip.shape[1] < self.tile_size:
                    padded_chip = np.zeros((self.tile_size, self.tile_size), dtype=img.dtype)
                    padded_chip[:chip.shape[0], :chip.shape[1]] = chip
                    chip = padded_chip
                
                # Save chip with embedded local coordinates for the Physics Engine mapping
                chip_filename = f"chip_{chip_count}_x{x}_y{y}.png"
                output_path = os.path.join(output_dir, chip_filename)
                
                cv2.imwrite(output_path, chip)
                chip_count += 1

        logging.info(f"Tiling complete. Extracted {chip_count} operational chips to {output_dir}")
        return chip_count

# --- Test Execution Block ---
if __name__ == "__main__":
    # Setup test directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TEST_INPUT = os.path.join(BASE_DIR, "media", "spills", "test_sar_scene.png")
    TEST_OUTPUT = os.path.join(BASE_DIR, "ml", "data", "processed_chips")

    # Create a dummy image if one doesn't exist just to test the pipeline
    if not os.path.exists(TEST_INPUT):
        os.makedirs(os.path.dirname(TEST_INPUT), exist_ok=True)
        dummy_img = np.random.randint(0, 255, (2000, 2000), dtype=np.uint8)
        cv2.imwrite(TEST_INPUT, dummy_img)
        logging.info("Created dummy 2000x2000 SAR image for testing.")

    # Run the Tiler
    tiler = SARTiler(tile_size=512)
    tiler.tile_image(TEST_INPUT, TEST_OUTPUT)
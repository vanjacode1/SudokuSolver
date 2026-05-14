import numpy as np
import torch
from model.digitnet import DigitNet

def load_digitnet(weights_path) -> DigitNet:
    """
    Load DigitNet weights and return an eval() model.
    """
    model = DigitNet()
    state_dict = torch.load(weights_path)
    model.load_state_dict(state_dict)
    model.eval()
    return model


@torch.no_grad()
def predict_digit_with_probs(img_array, model: DigitNet):
        """
        Predict a Sudoku digit from a single grayscale image array
        """
        img = img_array.astype(np.float32)
        if img.max() > 1.0:
            img = img / 255.0

        img = (img - 0.5) / 0.5

        x = torch.from_numpy(img).unsqueeze(0).unsqueeze(0)  
    
        # Forward pass
        logits = model(x)                    
        probs = torch.softmax(logits, dim=1)  
    
        probs = probs.squeeze(0)
          
        # Interpret results
        pred_class_index = int(torch.argmax(probs).item())  
        pred_digit = pred_class_index + 1                  
        confidence = float(probs[pred_class_index].item())  
    
        return pred_digit, confidence, probs
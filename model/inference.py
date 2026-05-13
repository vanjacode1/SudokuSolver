import numpy as np
import torch
from model.digitnet import DigitNet

def load_digitnet(weights_path) -> DigitNet:
    """
    Load DigitNet weights and return an eval() model on the chosen device.
    """
    model = DigitNet()
    state_dict = torch.load(weights_path)
    model.load_state_dict(state_dict)
    model.eval()
    return model


@torch.no_grad()
def predict_digit_with_probs(img_array, model: DigitNet):
        img = img_array.astype(np.float32)
        if img.max() > 1.0:
            img = img / 255.0

        x = torch.from_numpy(img).unsqueeze(0).unsqueeze(0)  # [1,1,28,28]
    
        # Forward pass
        with torch.no_grad():
            logits = model(x)                    
            probs = torch.softmax(logits, dim=1)  
    
        probs = probs.squeeze(0).cpu()  
          
        # Interpret results
        pred_class_index = int(torch.argmax(probs).item())  # 0 tm 8
        pred_digit = pred_class_index + 1                   # 1 tm 9
        confidence = float(probs[pred_class_index].item())  
    
        return pred_digit, confidence, probs
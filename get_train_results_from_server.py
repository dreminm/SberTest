from PIL import Image
from io import BytesIO
from pathlib import Path
import requests
import json
import numpy as np
import torch 
class TestDataset(torch.utils.data.Dataset):
    def __init__(self, test_dir):
        self.samples = []
        for subdir in test_dir.iterdir():
            for image_path in subdir.iterdir():
                self.samples.append(image_path)

    def __getitem__(self, idx):
        filename = self.samples[idx]
        image = Image.open(filename)
        image2bytes = BytesIO()
        image.save(image2bytes, format="PNG")
        image2bytes.seek(0)
        image_as_bytes = image2bytes.read()
        req = requests.post("http://localhost:8080/predictions/final_model", data=image_as_bytes)
        if req.status_code == 200: res = req.json()
        return (str(filename), res)

    def __len__(self):
        return len(self.samples)

def collate_fn(batch):
    return batch

if __name__=='__main__':
    test_dir = Path('Birds', 'test')
    dataset = TestDataset(test_dir)
    dataloader = torch.utils.data.DataLoader(dataset, num_workers=10, batch_size=1, collate_fn=collate_fn, prefetch_factor=10)
    answers = []
    for elem in dataloader:
        print(elem)
        answers.append(elem)
    print(answers)
    with open('test_answers.json', 'w') as wf:
        json.dump(answers, wf)


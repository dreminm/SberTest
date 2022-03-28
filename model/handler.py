from ts.torch_handler.image_classifier import ImageClassifier as ImgClsfr
import torch
from PIL import Image
import io

class ImageClassifier(ImgClsfr):
    topk = 5

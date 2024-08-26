# image_processor.py
import cv2
import numpy as np
from typing import Tuple, List


class ImageProcessor:
    @staticmethod
    def scale_image(image: np.ndarray, target_width: int, target_height: int) -> Tuple[np.ndarray, float]:
        img_height, img_width = image.shape[:2]
        width_ratio = target_width / img_width
        height_ratio = target_height / img_height
        scale_factor = min(width_ratio, height_ratio)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        scaled_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return scaled_image, scale_factor

    @staticmethod
    def extract_texture(image: np.ndarray, points: List[Tuple[float, float]], width: int, height: int) -> np.ndarray:
        src_pts = np.array(points, dtype=np.float32)
        dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return cv2.warpPerspective(image, M, (width, height))


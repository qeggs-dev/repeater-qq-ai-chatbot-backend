from enum import StrEnum

class ImageSize(StrEnum):
    AUTO = "auto"
    SIZE_1024x1024 = "1024x1024"
    SIZE_1536x1024 = "1536x1024"
    SIZE_1024x1536 = "1024x1536"
    SIZE_256x256 = "256x256"
    SIZE_512x512 = "512x512"
    SIZE_1792x1024 = "1792x1024"
    SIZE_1024x1792 = "1024x1792"
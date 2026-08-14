from pydantic import BaseModel

class GeneratedImagesConfig(BaseModel):
    base_dir: str = "./workspace/generated_images"
    download_chunk_size: int = 1024 * 1024 * 5
    file_name_prefix: str = "GeneratedImage_"
    save_file_suffix: str = ".png"
    image_timeout: int | float | None = 43200.0
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Union, Annotated
from enum import StrEnum

class ContentBlockType(StrEnum):
    TEXT = "text"
    IMAGE_URL = "image_url"
    VIDEO_URL = "video_url"
    INPUT_AUDIO = "input_audio"
    FILE = "file"


class TextBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )
    type: Literal[ContentBlockType.TEXT] = ContentBlockType.TEXT
    text: str = ""

class ImageUrlBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    url: str = ""

class ImageBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    type: Literal[ContentBlockType.IMAGE_URL] = ContentBlockType.IMAGE_URL
    image_url: ImageUrlBlock = Field(default_factory=ImageUrlBlock)

class VideoUrlBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    url: str = ""

class VideoBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    type: Literal[ContentBlockType.VIDEO_URL] = ContentBlockType.VIDEO_URL
    video_url: VideoUrlBlock = Field(default_factory=VideoUrlBlock)

class AudioDataBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    data: str = ""

class AudioBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    type: Literal[ContentBlockType.INPUT_AUDIO] = ContentBlockType.INPUT_AUDIO
    input_audio: AudioDataBlock = Field(default_factory=AudioDataBlock)

class FileDataBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    file_data: str = ""
    file_id: str = ""
    filename: str = ""

class FileBlock(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    type: Literal[ContentBlockType.FILE] = ContentBlockType.FILE
    file: FileDataBlock = Field(default_factory=FileDataBlock)

ContentBlock = Annotated[
    Union[
        TextBlock,
        ImageBlock,
        VideoBlock,
        AudioBlock,
        FileBlock
    ],
    "OpenAI API standard multimodal content blocks."
]
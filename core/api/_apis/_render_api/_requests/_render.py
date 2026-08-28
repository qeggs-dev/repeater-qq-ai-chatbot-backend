from pydantic import BaseModel

class RenderRequest(BaseModel):
    text: str
    style: str | None = None
    title: str | None = None
    image_expiry_time: float | None = None
    html_template: str | None = None
    width: int | None = None
    height: int | None = None
    direct_output: bool | None = None
    document_bottom_comment: str | None = None
    no_pre_labels: bool = False
    quality: int | None = None
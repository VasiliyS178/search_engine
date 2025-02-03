from pydantic import BaseModel


class DocumentAdd(BaseModel):
    file_path: str


class DocumentShow(BaseModel):
    file_path: str

    class Config:
        from_attributes = True

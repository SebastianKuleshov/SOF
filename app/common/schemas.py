from pydantic import BaseModel


class StorageItemBaseSchema(BaseModel):
    original_file_name: str


class StorageItemCreateSchema(StorageItemBaseSchema):
    stored_file_name: str
    storage_path: str

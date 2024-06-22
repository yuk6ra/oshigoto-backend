from fastapi import FastAPI
from pydantic import BaseModel


class MaterialBody(BaseModel):
    material_token_id: int
    material_contract_address: str # Address of the mirror nft contract
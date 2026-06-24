from pydantic import BaseModel, Field


class DiscoveryInput(BaseModel):
    task_id: str = None # change when using prefect
    input_filename: str    
    output_filename: str
    sensitivity: float = 0.75
    min_words: int = 80
    url: str

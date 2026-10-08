from fastapi import APIRouter
from .shared import  repos
import json
import ast
import logging

LOG = logging.getLogger(__name__)


api_files = APIRouter(prefix="/files")

@api_files.get("/get/{group}", operation_id="get_file")
async def get_file(group: str, file_path: str):
    """
    Retrieve a file from the repository.
    
    Args:
        file_path (str): The path to the file in the repository.
    
    Returns:
        File: The requested file.
    """
    response = repos.read_file(file_path, group)
    if response is None:
        return {"error": "File not found"}
    if not file_path.endswith(".json"):
        return response
    
    try:
        if response.startswith("{'"):
            LOG.debug(f"Content is in single quotes, converting to double quotes for file {file_path}")
            json_data = ast.literal_eval(response)
        else:
            json_data = json.loads(response)

        return json.dumps(json_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in file"}
        
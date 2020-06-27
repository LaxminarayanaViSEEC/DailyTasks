""" 
misc validations
"""
from pathlib import Path
from typing import Union

def check_file(file_path: Union[str, Path]):
    """check_file 
    Checks if the file exists in path
    
    Arguments:
        file_path {Union[str, Path]} -- File path to validate
    
    Returns:
        bool -- True if file is valid else False
    """

    file_path = Path(file_path)
    return file_path.is_file()
from typing import Dict
from PySide6.QtGui import QIcon
from pathlib import Path
from xml.dom import minidom


icon_folder = Path(__file__).with_name("icons")

def Icon(icon_name: str, color: str = "white"):
    if(icon_name):
        icon_name = f"{icon_name}_{color}"
        for file in icon_folder.glob('*.svg'):
            if(file.name.startswith(icon_name)):
                return QIcon(str(file))
    return None

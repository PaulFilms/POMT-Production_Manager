from enum import Enum

path_db = r"PPI.db"

class Alarmas(Enum):
    red     = ("🟥", 1)
    yellow  = ("🟨", 2)
    green   = ("🟩", 3)
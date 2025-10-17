"""
The system uses Code39 barcode to store identification data using 1D barcode.
The structure is as follows:
Example: aprj23
apr         j       23
appricot    jam     2023
See the dicts bellow for full table of options
"""
from datetime import datetime
import logging

produce = {
    "apr": "apricot",
    "str": "strawberry",
    "goo": "gooseberry",
    "tom": "tomato"
}

types = {
  "j": "jam",
  "c": "compote",
  "s": "spread",
  "p": "pickle",
  "x": "chilli",
  "k": "ketchup"
}

logger = logging.getLogger("pantry")

def barcode_to_json(barcode: str) -> dict:
    # validate fruit/veggie, save the full name
    if barcode[:3] in produce:
        produce_name: str = produce[barcode[:3]]
    else:
        logger.error(f"Unknown produce name: {barcode[:3]}")
        return {}

    # validate and save the preserve type
    if barcode[3] in types:
        type_name = types[barcode[3]]
    else:
        logger.error(f"Unknown type: {barcode[3]}")
        return {}

    # validate and save the year
    if barcode[4:6].isnumeric():
        year = int(barcode[4:6])
        if year >  datetime.now().year - 2000:
            year += 1900
        else:
            year += 2000
    else:
        logger.error(f"Unknown year: {barcode[4:6]}")
        return {}

    return {"preserve_type": type_name, "main_ingredient": produce_name, "year": year}
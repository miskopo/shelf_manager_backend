"""
Barcode parsing for the pantry system.

Uses Code39 1D barcodes with the structure:
Example: aprj23
apr         j       23
apricot     jam     2023
"""

import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logger = logging.getLogger("pantry")
logger.setLevel(logging.INFO)

load_dotenv()

DB_PASS = os.getenv("DB_PASS")
DB_USER = os.getenv("DB_USER")
DB_URL = os.getenv("DB_URL")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_URL}/pantrydb")

# Cache dictionaries for fast lookup
PRODUCE: dict[str, str] = {}
TYPES: dict[str, str] = {}

def load_codes():
    """Load produce and preserve type codes from the database into memory."""
    global PRODUCE, TYPES
    with engine.connect() as conn:
        PRODUCE = dict(conn.execute(text("""SELECT code, name FROM produce""")).fetchall())
        TYPES = dict(conn.execute(text("""SELECT code, name FROM preserve_types""")).fetchall())
    logger.info(f"Loaded {len(PRODUCE)} produce codes and {len(TYPES)} types.")

# Load codes at module import
load_codes()

def barcode_to_json(barcode: str) -> dict:
    """
    Convert a barcode string to a dictionary suitable for CRUD functions.

    :param barcode: 6-character string (e.g., 'aprj23')
    :return: dict with keys 'preserve_type', 'main_ingredient', 'year'; empty dict if invalid
    """
    if len(barcode) != 6:
        logger.error(f"Invalid barcode length: {barcode}")
        return {}

    # Parse produce
    produce_code = barcode[:3]
    produce_name = PRODUCE.get(produce_code)
    if not produce_name:
        logger.error(f"Unknown produce code: {produce_code}")
        return {}

    # Parse preserve type
    type_code = barcode[3]
    type_name = TYPES.get(type_code)
    if not type_name:
        logger.error(f"Unknown preserve type code: {type_code}")
        return {}

    # Parse year
    year_code = barcode[4:6]
    if not year_code.isnumeric():
        logger.error(f"Invalid year code: {year_code}")
        return {}
    year = int(year_code)
    current_year = datetime.now().year % 100
    if year > current_year:
        year += 1900
    else:
        year += 2000

    return {
        "main_ingredient": produce_name,
        "preserve_type": type_name,
        "year": year
    }
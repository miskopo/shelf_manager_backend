"""
Pantry Scanner Daemon
Continuously reads barcode input from /dev/input/eventX, converts to preserve info, and updates the DB.
"""

import os

from dotenv import load_dotenv
from evdev import InputDevice, categorize, ecodes
from sqlalchemy import create_engine, text

from logger import logger
from pantry.barcode import barcode_to_json
from pantry.db import add_preserve, remove_preserve

load_dotenv()

DEVICE_PATH = os.getenv("SCANNER_EVENT")


load_dotenv()

DB_PASS = os.getenv("DB_PASS")
DB_USER = os.getenv("DB_USER")
DB_URL = os.getenv("DB_URL")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_URL}/pantrydb")

def read_mode() -> str:
    """Read current mode (add/remove)."""
    try:
        with engine.connect() as conn:
            mode = conn.execute(text("""SELECT mode FROM mode""")).fetchone()[0]
            logger.debug(f"Reading mode: {mode}")
            return mode if mode in ("add", "remove") else "remove"
    except FileNotFoundError:
        logger.error("Unable to read mode file, defaulting to remove")
        return "remove"


def set_mode(new_mode: str) -> None:
    """set add/remove mode (triggered by special barcodes)."""
    with engine.begin() as conn:
        result = conn.execute(text("""UPDATE mode SET mode = :new_mode"""), {"new_mode": new_mode})  # safe to update whole table
        assert result.rowcount in [0, 1]
    logger.info(f"Switched mode to {new_mode.upper()}")


def handle_barcode(barcode: str):
    """Interpret and act on scanned barcode."""
    barcode = barcode.strip()
    logger.debug(f"Processing barcode: {barcode}")
    if not barcode:
        return

    # reserved barcode for toggling mode
    if barcode == "add":
        set_mode("add")
        return
    if barcode == "remove":
        set_mode("remove")
        return

    preserve = barcode_to_json(barcode)
    if not preserve:
        logger.warning(f"Unrecognized barcode: {barcode}")
        return

    mode = read_mode()
    if mode == "add":
        add_preserve(preserve)
        logger.info(f"Added: {preserve}")
    else:
        remove_preserve(preserve)
        logger.info(f"Removed: {preserve}")


def run():

    device = InputDevice(DEVICE_PATH)
    logger.info(f"Listening on {device.name}...")

    barcode = ""
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            if data.keystate == 1:  # Key down
                if data.keycode == "KEY_ENTER":
                    logger.debug(f"Scanned: {barcode}")
                    handle_barcode(barcode)
                    barcode = ""
                elif len(data.keycode) == 5 and data.keycode.startswith("KEY_"):
                    barcode += data.keycode[-1].lower()


if __name__ == "__main__":
    run()
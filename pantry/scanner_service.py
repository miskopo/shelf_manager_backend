"""
Pantry Scanner Daemon
Continuously reads barcode input from /dev/hidraw*, converts to preserve info, and updates the DB.
"""

import logging
import os
import time

from dotenv import load_dotenv

from pantry.db import add_preserve, remove_preserve
from pantry.barcode import barcode_to_json

load_dotenv()

DEVICE_PATH = os.getenv("SCANNER_DEVICE")
MODE_FILE = "/var/lib/pantry/mode"  # stores 'add' or 'remove'
os.makedirs("/var/lib/pantry", exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pantry.scanner")


def read_mode() -> str:
    """Read current mode (add/remove)."""
    try:
        with open(MODE_FILE, "r") as f:
            mode = f.read().strip().lower()
            return mode if mode in ("add", "remove") else "remove"
    except FileNotFoundError:
        logger.error("Unable to read mode file, defaulting to remove")
        return "remove"


def set_mode(new_mode: str) -> None:
    """set add/remove mode (triggered by special barcodes)."""
    with open(MODE_FILE, "w") as f:
        f.write(new_mode)
    logger.info(f"Switched mode to {new_mode.upper()}")


def handle_barcode(barcode: str):
    """Interpret and act on scanned barcode."""
    barcode = barcode.strip()
    if not barcode:
        return

    # reserved barcode for toggling mode
    if barcode == "add":
        set_mode("add")
        return
    if barcode == "remove":
        set_mode("remove")

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
    logger.info(f"Listening on {DEVICE_PATH}...")
    while True:
        try:
            with open(DEVICE_PATH, "r") as dev:
                buffer = ""
                while True:
                    ch = dev.read(1)
                    if not ch:
                        time.sleep(0.01)
                        continue

                    if ch in ("\n", "\r"):
                        handle_barcode(buffer)
                        buffer = ""
                    else:
                        buffer += ch
        except Exception as e:
            logger.error(f"Device read error: {e}")
            time.sleep(2)


if __name__ == "__main__":
    run()
"""CRUD operations for the pantry database"""
import os
from logging import getLogger
from typing import Union

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logger = getLogger("pantry")

load_dotenv()

DB_PASS = os.getenv('DB_PASS')
DB_USER = os.getenv('DB_USER')
DB_URL = os.getenv('DB_URL')

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_URL}/pantrydb")

def add_preserve(preserve: dict[str, Union[str, int]]) -> int:
    """
    Adds or updates preserve quantity atomically using PostgreSQL ON CONFLICT.
    :param preserve: dictionary of type, main_ingredient and year
    :return: number of preserves added or modified (should be one if successful)
    """
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                 INSERT INTO preserves (type, main_ingredient, year, quantity)
                 VALUES (:type, :main_ingredient, :year, 1)
                 ON CONFLICT (type, main_ingredient, year)
                     DO UPDATE SET quantity = preserves.quantity + 1;
                 """),
            preserve
        )
        return result.rowcount


def remove_preserve(preserve: dict[str, Union[str, int]]) -> int:
    """
    Atomically decrease quantity by 1 or delete row if quantity reaches zero.
    :param preserve: dictionary of type, main_ingredient and year
    :return: number of preserves added or modified (should be one if successful)
    """
    with engine.begin() as conn:
        # Try to decrement quantity if > 1
        result = conn.execute(
            text("""
                 UPDATE preserves
                 SET quantity = quantity - 1
                 WHERE type = :type AND main_ingredient = :main_ingredient AND year = :year AND quantity > 1;
                 """),
            preserve
        )
        if result.rowcount == 0:
            # No row updated → either quantity = 1 or row missing → delete
            result = conn.execute(
                text("""
                     DELETE FROM preserves
                     WHERE type = :type AND main_ingredient = :main_ingredient AND year = :year AND quantity = 1;
                     """),
                preserve
            )
        return result.rowcount


def get_preserve(preserve: dict)-> Union[tuple, None]:
    """
    Get preserve row from the database.

    :param preserve: dictionary of type, main_ingredient and year
    :return: tuple of  a row with found preserve, None if not found
    """
    with engine.connect() as conn:
        result = conn.execute(text("""SELECT * FROM preserves
                                      WHERE
                                          type = :type
                                        AND main_ingredient = :main_ingredient
                                        AND year = :year;"""),
                              preserve)
        rows = result.fetchone()
    return rows
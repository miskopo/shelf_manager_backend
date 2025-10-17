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
                VALUES (:type, :main, :year, 1)
                ON CONFLICT (type, main_ingredient, year)
                DO UPDATE SET quantity = preserves.quantity + 1;
            """),
            {
                "type": preserve["type"],
                "main": preserve["main_ingredient"],
                "year": preserve["year"]
            }
        )
        return result.rowcount


def remove_preserve(preserve: dict[str, Union[str, int]]):
    """
    Decreases quantity of an existing preserve in the database or removes entry completely if only one remains.
    :param preserve: dictionary of type, main_ingredient and year
    :return: number of preserves removed or modified (should be one if successful)
    """
    # first check if more then one remains
    preserve_to_remove = get_preserve(preserve)
    if len(preserve_to_remove) == 0:
        logger.error("No preserve to remove, database in inconsistent state")
        return -1
    if len(preserve_to_remove) == 1:
        current_stock = preserve_to_remove[0][4] # take just the quantity
        if current_stock > 1:
            return update_quantity(preserve, -1)
        with engine.connect() as conn:
            result = conn.execute(text("""
                                       DELETE FROM preserves 
                                       WHERE type = :type AND main_ingredient = :main AND year = :year 
                                         AND quantity = 1;"""),
                                  {"type": preserve['type'],
                                   "main": preserve['main_ingredient'],
                                   "year": preserve['year']})
            conn.commit()
        return result.rowcount

    # otherwise something is wrong
    logger.error("Too many preserve to remove, database in inconsistent state")
    return -1


def update_quantity(preserve: dict[str, Union[str, int]], by_quantity: int) -> int:
    """
    Updates quantity of an existing preserve in the database.
    :param preserve: dictionary of type, main_ingredient and year
    :param by_quantity: number of preserves to be added
    :return: number of preserves updated (should be one if successful)
    """
    with engine.connect() as conn:
        result = conn.execute(text("""
                                   UPDATE  preserves SET quantity = quantity + :by_quantity 
                                   WHERE 
                                       type = :type 
                                     AND main_ingredient = :main 
                                     AND year = :year;"""),
                                   {"by_quantity": by_quantity,
                                    "type": preserve['type'],
                                    "main": preserve['main_ingredient'],
                                    "year": preserve['year']})
        conn.commit()
    return result.rowcount


def get_preserve(preserve: dict) -> list[tuple]:
    """
    Get preserve row from the database.

    :param preserve: dictionary of type, main_ingredient and year
    :return: list of found preserves, should be one if successful
    """
    with engine.connect() as conn:
        result = conn.execute(text("""SELECT * FROM preserves
                                      WHERE 
                                          type = :type 
                                        AND main_ingredient = :main 
                                        AND year = :year;"""),
                              {"type": preserve['type'],
                               "main": preserve['main_ingredient'],
                               "year": preserve['year']})
        rows = result.fetchall()
    return rows
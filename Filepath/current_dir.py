from pathlib import Path

""" Get directory of *this* file """

BASE_DIR = Path(__file__).resolve(strict=True).parent

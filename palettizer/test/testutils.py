import os
from pathlib import Path


def get_test_resource(rel_path: str) -> Path:
    test_dir = Path(os.path.realpath(__file__)).parent.absolute()
    return test_dir.joinpath("resources/" + rel_path)

from __future__ import annotations

from pyspark.sql import DataFrame


def to_file(df: DataFrame, path: str, fmt: str, save_mode: str):
    df.write.format(fmt).mode(save_mode).save(path)

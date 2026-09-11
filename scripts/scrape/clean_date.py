#!/usr/bin/env python3
"""
Normalise first_date_appeared column to YYYY-MM format.
Usage: python clean_date.py <input_csv> [output_csv]
"""
import sys
import pandas as pd

input_path = sys.argv[1] if len(sys.argv) > 1 else None
output_path = sys.argv[2] if len(sys.argv) > 2 else input_path

if not input_path:
    print("Usage: python clean_date.py <input_csv> [output_csv]", file=sys.stderr)
    sys.exit(1)

df = pd.read_csv(input_path)
df['first_date_appeared'] = pd.to_datetime(
    df['first_date_appeared'], format='mixed', errors='coerce'
)
df['first_date_appeared'] = df['first_date_appeared'].dt.strftime('%Y-%m')
df.to_csv(output_path, index=False)
print(df['first_date_appeared'].head(20))

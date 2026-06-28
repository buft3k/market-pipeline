import glob
import os
import pandas as pd


def load_data(data_dir: str) -> pd.DataFrame:
    data_files = glob.glob(f"{data_dir}/*.csv")

    frames = []
    for file in data_files:
        try:
            basename = os.path.basename(file)       # "SP500.csv"
            name, __ = os.path.splitext(basename)  # ("SP500", ".csv")
            ticker = name                           # "SP500"

            df = pd.read_csv(file)
            if "observation_date" not in df.columns or ticker not in df.columns:
                print(f"Warning: skipping {file} — expected columns 'observation_date' and '{ticker}'")
                continue

            df["ticker"] = ticker 
            df = df.rename(columns={ticker: "value"})  #rename ticker column to value

            frames.append(df)
        except Exception as e:
            print(f"Warning: skipping {file} — could not parse file: {e}")
    if not frames:
      raise ValueError(f"No valid CSV files found in {data_dir}")
      
    return pd.concat(frames, ignore_index=True)

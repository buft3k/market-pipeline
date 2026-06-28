import argparse
from config import load_config
from extract import load_data
from transform import apply_checks


def main():
    parser = argparse.ArgumentParser(description="Market data pass/fail check pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    df = load_data(config["data_dir"])
    results = apply_checks(df, config)
    results.to_csv(config["output_file"], index=False)
    print(f"Done. {len(results)} flags written to {config['output_file']}")


if __name__ == "__main__":
    main()

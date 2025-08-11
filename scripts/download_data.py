from datasets import load_dataset


def download_data(n_samples: int = 300):
    """
    Download de dataset do Wikipedia em português.

    Args:
        n_samples: Número de amostras a serem baixadas.

    Returns:
        None
    """
    ds = load_dataset("TucanoBR/wikipedia-PT", split=f"train[:{n_samples}]")
    print(f"Dataset loaded with {len(ds)} samples")
    ds.to_json(f"data/raw/wikipedia-PT-{n_samples}.jsonl", force_ascii=False)


if __name__ == "__main__":
    download_data()

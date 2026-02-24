import argparse
import os
from huggingface_hub import snapshot_download


def main() -> None:
    parser = argparse.ArgumentParser(description="Download lightweight Hugging Face model for offline/local mode.")
    parser.add_argument("--model-id", default="distilgpt2", help="Hugging Face model ID")
    parser.add_argument("--output-dir", default="models/distilgpt2", help="Local folder where the model will be stored")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.output_dir)
    os.makedirs(target_dir, exist_ok=True)

    print(f"Downloading {args.model_id} into {target_dir} ...")
    snapshot_download(repo_id=args.model_id, local_dir=target_dir, local_dir_use_symlinks=False)
    print("Done.")


if __name__ == "__main__":
    main()

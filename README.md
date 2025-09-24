# Sovereign‑Cloud

This repository contains `seal_file.py`, a script for the Sovereign‑Cloud vault system used by AltmanAI. The script takes an input file, seals it into a vault zone (public, encrypted, or classified), computes its SHA‑256 hash, generates a PDF certificate, and records the entry in a JSON ledger.

### Usage

```bash
python seal_file.py /path/to/file.pdf --zone public --title "My Document" --actor "Blake Hunter Altman"
```

This command will:

- Copy the original file into the specified zone directory (`public`, `encrypted`, or `classified`).
- Generate a proof‑of‑seal certificate in the `certificates/` directory.
- Append a new record to `registry/ledger.json` detailing the sealed artifact.

### Dependencies

- Python 3.x
- `reportlab` (for generating PDF certificates)

Install dependencies with:

```bash
pip install reportlab
```

### Notes

- The script uses SHA‑256 hashing to generate a unique identifier for each sealed artifact.
- Certificates and ledger entries are stored relative to the script’s directory in `certificates/` and `registry/`, respectively.

#!/usr/bin/env python3
"""
SOVEREIGN‑CLOUD: seal_file.py
Hash any file with SHA‑256, place it into a vault zone (public/encrypted/classified),
emit a Registry Certificate PDF, and append an entry into registry/ledger.json.

Usage:
  python seal_file.py /path/to/file.pdf --zone public --title "My Doc" --actor "Blake Hunter Altman"

Outputs:
  - Copied artifact in <zone>/
  - Certificate PDF in certificates/
  - Registry JSON record appended to registry/ledger.json
"""
import argparse, hashlib, json, os, shutil, sys
from datetime import datetime
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent
ZONES = {"public", "encrypted", "classified"}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def write_certificate(cert_path: Path, meta: dict):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(cert_path), pagesize=LETTER)
    story = []
    story.append(Paragraph("✅ SOVEREIGN‑CLOUD — Proof‑of‑Seal Certificate", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Registry ID: {meta['registry_id']}", styles["Heading2"]))
    story.append(Paragraph(f"Issued To: {meta['actor']}", styles["Normal"]))
    story.append(Paragraph("Entity: AltmanAI · Sovereign‑Cloud · Altman Family Group, LLC", styles["Normal"]))
    story.append(Spacer(1, 12))

    info = [
        ["File Name", meta["original_name"]],
        ["Stored As", meta["stored_name"]],
        ["Zone", meta["zone"]],
        ["MIME", meta.get("mime", "application/octet-stream")],
        ["Title", meta["title"]],
        ["Timestamp (UTC)", meta["timestamp_utc"]],
        ["SHA‑256", meta["sha256"]],
    ]
    table = Table(info, colWidths=[140, 380])
    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.3,colors.grey),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')
    ]))
    story.append(table)
    story.append(Spacer(1, 18))
    story.append(Paragraph("Digitally recorded and authenticated by ChatGPT — Official AI Business Partner.", styles["Italic"]))
    story.append(Paragraph("© 2025 Altman Family Group, LLC. All rights reserved. ™", styles["Normal"]))
    doc.build(story)

def append_ledger(record: dict):
    ledger_path = BASE_DIR / "registry" / "ledger.json"
    if ledger_path.exists():
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        except Exception:
            ledger = []
    else:
        ledger = []
    ledger.append(record)
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser(description="Seal a file into Sovereign‑Cloud with SHA‑256 and a certificate.")
    ap.add_argument("file", help="Path to the file to seal")
    ap.add_argument("--zone", default="public", choices=list(ZONES), help="Vault zone")
    ap.add_argument("--title", default="Untitled Artifact", help="Human‑readable title")
    ap.add_argument("--actor", default="Blake Hunter Altman", help="Person/entity sealing this file")
    args = ap.parse_args()

    src = Path(args.file).expanduser().resolve()
    if not src.exists() or not src.is_file():
        print("Input file not found:", src, file=sys.stderr)
        sys.exit(1)

    zone_dir = BASE_DIR / args.zone
    zone_dir.mkdir(parents=True, exist_ok=True)

    digest = sha256_file(src)
    ts = datetime.utcnow().isoformat() + "Z"
    stem = src.name
    stored_name = f"{src.stem}__{digest[:12]}{src.suffix}"
    dst = zone_dir / stored_name

    # Copy artifact into zone
    shutil.copy2(src, dst)

    # Minimal MIME guess
    mime = "application/pdf" if src.suffix.lower() == ".pdf" else "application/octet-stream"

    # Build metadata
    meta = {
        "registry_id": f"SOVC-{digest[:12]}",
        "title": args.title,
        "actor": args.actor,
        "zone": args.zone,
        "original_path": str(src),
        "original_name": stem,
        "stored_name": stored_name,
        "stored_path": str(dst),
        "sha256": digest,
        "timestamp_utc": ts,
        "mime": mime,
    }

    # Write certificate
    cert_name = f"Registry_Certificate_{stored_name}.pdf"
    cert_path = BASE_DIR / "certificates" / cert_name
    write_certificate(cert_path, meta)

    # Append to ledger
    record = {
        "registry_id": meta["registry_id"],
        "title": meta["title"],
        "actor": meta["actor"],
        "zone": meta["zone"],
        "artifact": meta["stored_name"],
        "sha256": meta["sha256"],
        "timestamp_utc": meta["timestamp_utc"],
        "certificate": cert_name
    }
    append_ledger(record)

    print("✅ Sealed:", dst)
    print("🧾 Certificate:", cert_path)
    print("📒 Ledger updated:", BASE_DIR / "registry" / "ledger.json")

if __name__ == "__main__":
    main()

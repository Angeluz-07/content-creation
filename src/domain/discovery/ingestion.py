import uuid
from pathlib import Path
import pandas as pd


def get_uuid_from_string(seed_string: str) -> uuid.UUID:
    # Use the standard DNS namespace as a base
    namespace = uuid.NAMESPACE_DNS
    # Generate a deterministic UUID version 5
    return uuid.uuid5(namespace, seed_string)


def add_samples_from_transcriptions(directory_path: str | Path, vector_store):
    csv_path = Path(directory_path) / "metadata.csv"
    if not csv_path.exists():
        print(f"metadata.csv not found.")
        return

    df = pd.read_csv(csv_path)
    if "transcription" not in df.columns:
        print(f"transcription column not found.")
        return

    added_count = 0
    for _, row in df.iterrows():
        text = str(row.get("transcription", "")).strip()
        if not text or text == "nan":  # covers empty rows
            continue

        metadata = {
            "filename": str(row.get("filename", "na")),
            "duration": float(row.get("duration", 0.0)),
            "text": text,
            "show": str(row.get("show", "na")),
        }

        # ID compatible con Qdrant (UUID v5)
        text_id = get_uuid_from_string(text)
        vector_store.add(id=text_id, text=text, metadata=metadata)
        added_count += 1

    print(f"Procesado exitosamente: {added_count} vectores enviados a indexar.")

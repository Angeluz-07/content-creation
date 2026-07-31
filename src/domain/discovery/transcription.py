from pathlib import Path
import pandas as pd
from typing import Callable


def gen_video_transcriptions(directory_path: str | Path, transcriber_fn: Callable):
    folder = Path(directory_path)
    csv_path = folder / "metadata.csv"
    mp4_files = {f.stem: f for f in folder.glob("*.mp4")}

    # 1. Cargar CSV existente o crear base desde los archivos mp4
    df = (
        pd.read_csv(csv_path)
        if csv_path.exists()
        else pd.DataFrame({"filename": list(mp4_files.keys())})
    )

    if "transcription" not in df.columns:
        df["transcription"] = ""

    # 2. Transcribir solo los registros sin texto previo
    transcriptions = []
    for _, row in df.iterrows():
        text = str(row["transcription"]).strip()

        if not text:
            file_path = mp4_files.get(str(row["filename"]))
            res = transcriber_fn(str(file_path)) if file_path else {}
            text = res.get("text", "") if isinstance(res, dict) else ""

        transcriptions.append(text)

    # 3. Guardar cambios
    df["transcription"] = transcriptions
    df.to_csv(csv_path, index=False)
    print(f"Procesado: {csv_path}")

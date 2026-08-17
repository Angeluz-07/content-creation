import asyncio
import subprocess
import json
import sys
from typing import List


def run_subprocess(command: List[str], show_live_output: bool = True) -> str:
    print(f"Starting command call (via Sync Subprocess): ")
    print(command)
    # Popen starts the process asynchronously so we can stream its output
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout to preserve chronological order
        text=True,
        bufsize=1,  # Line-buffered output
        errors="ignore",
    )

    captured_output = []

    # Stream output line-by-line in real time
    if process.stdout:
        for line in process.stdout:
            captured_output.append(line)
            if show_live_output:
                # Use sys.stdout.write to preserve exact CLI formatting (handles \r progress bars)
                sys.stdout.write(line)
                sys.stdout.flush()

    process.wait()
    full_output = "".join(captured_output)

    if process.returncode != 0:
        print("\n" + "=" * 50)
        print("DETAILED ERROR OUTPUT:")
        print("=" * 50)
        print(full_output.strip())
        print("=" * 50 + "\n")

        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=command,
            output=full_output,
            stderr="",
        )

    print("\nSuccess command call via Synchronous Subprocess")
    return full_output


async def run_async_subprocess(
    command: List[str], show_live_output: bool = True
) -> str:
    print(f"Starting command call (via Async Subprocess): ")
    print(command)

    # Redirigimos stderr a stdout igual que en tu versión síncrona
    process = await asyncio.create_subprocess_exec(
        command[0],
        *command[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,  # Fusiona canales cronológicamente
    )

    captured_output = []

    # Leemos línea por línea en tiempo real de forma asíncrona
    if process.stdout:
        async for line_bytes in process.stdout:
            # Decodificamos ignorando errores tal como tu versión síncrona
            line = line_bytes.decode(errors="ignore")
            captured_output.append(line)

            if show_live_output:
                sys.stdout.write(line)
                sys.stdout.flush()

    await process.wait()
    full_output = "".join(captured_output)

    if process.returncode != 0:
        # print("\n" + "=" * 50)
        # print("DETAILED ERROR OUTPUT:")
        # print("=" * 50)
        # print(full_output.strip())
        # print("=" * 50 + "\n")

        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=command,
            output=full_output,
            stderr="",
        )

    print("\nSuccess command call via Async Subprocess")
    return full_output


def read_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        result = json.load(file)
    return result


def save_json(data, output_path: str):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

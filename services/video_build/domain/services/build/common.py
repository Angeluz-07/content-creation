import asyncio
import subprocess

async def run_async_subprocess(command: str):
    print(f"Starting command call (via Async Subprocess): ")
    process = await asyncio.create_subprocess_exec(
        command[0],
        *command[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Esperamos a que el proceso muera físicamente en el Kernel
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=command,  # O la variable donde guardes el comando ejecutado
            stderr=stderr.decode().strip(),
        )

    print("Success command call via Async Subprocess")
import asyncio
import subprocess

def run_subprocess(command: list):
    print("Starting command call (via Synchronous Subprocess):")
    
    # Ejecución síncrona capturando strings directamente (text=True)
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # Esto evita tener que usar .decode()
        errors="ignore"
    )
    
    if result.returncode != 0:
        # 1. Imprimimos el error real de FFmpeg directamente en la consola antes de morir
        print("\n" + "="*50)
        print("DETAILED ERROR OUTPUT:")
        print("="*50)
        print(result.stderr.strip())
        print("="*50 + "\n")
        
        # 2. Lanzamos la excepción con los detalles incluidos
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=command,
            output=result.stdout,
            stderr=result.stderr
        )
        
    print("Success command call via Synchronous Subprocess")
    return result.stdout

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
        print("\n" + "="*50)
        print("DETAILED ERROR OUTPUT:")
        print("="*50)
        print(stderr.decode().strip())
        print("="*50 + "\n")
        
        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=command,  # O la variable donde guardes el comando ejecutado
            stderr=stderr.decode().strip(),
        )

    print("Success command call via Async Subprocess")

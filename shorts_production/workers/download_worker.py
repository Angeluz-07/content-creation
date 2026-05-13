import asyncio
# Cambiamos RedisAsyncBroker por ListQueueBroker o RedisStreamBroker
# RedisStreamBroker es el más moderno y recomendado
from taskiq_redis import RedisStreamBroker 
from taskiq import TaskiqEvents

# 1. Usamos la clase que la librería encontró
broker = RedisStreamBroker("redis://localhost:6379")

@broker.task
async def download_task(name: str):
    print(f"--- [TASKIQ] ---")
    print(f"Hola {name}, procesando descarga de forma asíncrona.")
    
    # Aquí puedes usar anyio para FFmpeg como hablamos antes
    # await anyio.run_process(["ffmpeg", ...])
    
    #await asyncio.sleep(2)  # Simulamos trabajo
    print("Tarea completada con éxito.")
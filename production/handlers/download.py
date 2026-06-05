# app/handlers/downloads.py
from faststream.redis import RedisRouter
from context import download_projector

router = RedisRouter()


@router.subscriber("download:completed")
async def project_download(payload: dict):
    params = payload["download"]
    # todo fix: there is a race condition. projector
    # tries to add an item but is based one event
    # table, this runs quicke than the other,
    # so doesnt fint the event succss on table
    download_projector.project_direct(params=params)

from services.short_producer_service import ShortProducer
from dbs.mongo_client import get_mongo_client
from dbs.config_repository import MongoConfigRepository
from config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT

#from dbs.interfaces import InMemoryDummyRepository
#config_repo = InMemoryDummyRepository()


mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
config_repo = MongoConfigRepository(mongo_client, db_name="cc_db", collection_name="short_configs")


short_producer = ShortProducer(config_repo=config_repo)

import asyncio

from handlers.socket_handler import SocketHandler
from services.sync_service import SyncService

# initialize DB
from repository.engine import engine

# need to pass a sync handler instance..
sync_service = SyncService()
socket_handler = SocketHandler(sync_service, 8765)
    


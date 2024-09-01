import asyncio
import json
import traceback
from websockets.asyncio.server import serve


class SocketHandler:
    '''
    A stateful handler of socket connections
    '''
    connected_clients = set()

    def __init__(self, sync_service, port):
        self.sync_service = sync_service
        self.port = port
        asyncio.run(self.start_server())


    async def start_server(self):
        async with serve(self.client_connect, "0.0.0.0", self.port):
            await asyncio.get_running_loop().create_future()

    async def client_connect(self, websocket):
        '''
        connect a new client
        '''
        print("New client connected")
        self.connected_clients.add(websocket)

        #connection close handlers
        closed = asyncio.ensure_future(websocket.wait_closed())
        closed.add_done_callback(lambda task: self.client_disconnect(websocket))

        try:
            async for message in websocket:
                await self.handle_message(message, websocket)

        except Exception as e:
            # More granular exception handling
            print("An unexpected error occured.")
            traceback.print_exc()


    async def handle_message(self, message, websocket):
        # schema validation (and content checks) could work nicely for the JSON messages
        data = json.loads(message)
            
        # Check the the message type, could be hidden behind it's own class group with related logic
        if 'type' not in data:
            await websocket.send(json.dumps({"error": "Invalid message format"}))

        message_type = data.get('type')

        match message_type:

            case 'hello_sync':
                date_time = data.get("dateTime")

                updated_batches = self.sync_service.get_batches_since_datetime(date_time)

                await websocket.send(json.dumps(updated_batches))

            case 'push_sync':
                id = data.get("id", None)
                new_client_data = data.get("batch")
                change = data.get("change")

                updated_synced_record = self.sync_service.push_batch(id, change, new_client_data)

                for other_websockets in self.connected_clients:
                    await other_websockets.send(json.dumps(updated_synced_record.to_json()))
    

    def client_disconnect(self, websocket):
        print("Client disconnected")
        self.connected_clients.remove(websocket)

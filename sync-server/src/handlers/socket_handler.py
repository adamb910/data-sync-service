import json
import asyncio
import traceback
from websockets.asyncio.server import serve

import constants


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
        try:
            #TODO: schema validation (and content checks) could work nicely for the JSON messages
            data = json.loads(message)
                
            #TODO: Check the the message type, could be hidden behind it's own class group with related logic
            # This would completely decouple the layer which deals with the messaging protocol from the actual application logic
            if constants.MESSAGE_TYPE not in data:
                raise ValueError("Incorrect message format!")

            message_type = data.get(constants.MESSAGE_TYPE)

            match message_type:

                case constants.HELLO_MESSAGE:
                    #TODO: input should be a unix timestamp instead of a datetime iso string
                    date_time = data.get(constants.DATETIME)

                    updated_batches = self.sync_service.get_batches_since_datetime(date_time)

                    await websocket.send(json.dumps(updated_batches))

                case constants.PUSH_MESSAGE:
                    id = data.get(constants.ID, None)
                    new_client_data = data.get(constants.BATCH_DATA)
                    change = data.get(constants.BATCH_CHANGE_METHOD)

                    updated_synced_record = self.sync_service.push_batch(id, change, new_client_data)

                    for other_websockets in self.connected_clients:
                        await other_websockets.send(json.dumps(updated_synced_record))
        except ValueError as value_error:
            await websocket.send(json.dumps({"error": "Invalid message format"}))
        except Exception as e:
            await websocket.send(json.dumps({"error": str(e)}))
            print(e)
            #TODO: proper logging solution with appropriately chosen log levels..
            traceback.print_exc()
    

    def client_disconnect(self, websocket):
        self.connected_clients.remove(websocket)

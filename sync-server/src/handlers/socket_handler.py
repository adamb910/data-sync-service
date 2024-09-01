import asyncio
import json
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
        try:
            async for message in websocket:
                await self.handle_message(message)

        except websockets.exceptions.ConnectionClosed as e:
            print("Client disconnected")
            self.connected_clients.remove(websocket)
        except:
            # More granular error handling
            print("An unexpected error occured.")


    async def handle_message(self, message, websocket):
        data = json.loads(message)
            
        # Check the the message type, could be hidden behind it's own class group with related logic
        if 'type' not in data:
            await websocket.send(json.dumps({"error": "Invalid message format"}))

        message_type = data.get('type')

        match message_type:
            case 'hello_sync':
                date_time = data.get("dateTime")
                updated_batches = self.sync_service.get_batches_since_datetime(date_time)
                #TODO: clarify data structure here
                websocket.send(updated_batches)
            case 'push_sync':
                updated_data = data.get("batch")
                self.sync_service.push_update(updated_data)
                #TODO: clarify data structures here
                websocket.send({"message": "ACK"})
                for other_websockets in self.connected_clients:
                    other_websockets.send(updated_data)
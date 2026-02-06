import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RealtimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Aceita a conexão WebSocket
        await self.accept()
        # Adiciona o cliente ao grupo "dashboard"
        await self.channel_layer.group_add("dashboard", self.channel_name)

    async def disconnect(self, close_code):
        # Remove do grupo ao desconectar
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    async def receive(self, text_data):
        # Se receber mensagem do frontend (opcional)
        pass

    async def send_update(self, event):
        # Método chamado pelo layer para enviar dados ao frontend
        message = event['message']
        await self.send(text_data=json.dumps(message))
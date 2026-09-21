import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class TransactionLiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("[WEBSOCKET] Client connected 📡")
        await self.send(text_data=json.dumps({
            "type": "WELCOME",
            "message": "Connected to FinTrend Live Transaction & Compliance WebSocket Feed 🚀"
        }))

    async def disconnect(self, close_code):
        print(f"[WEBSOCKET] Client disconnected (code: {close_code}) 🔌")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data.get("type")
            if msg_type == "PING":
                await self.send(text_data=json.dumps({"type": "PONG"}))
        except Exception as e:
            pass

    async def broadcast_transaction(self, event):
        await self.send(text_data=json.dumps({
            "type": "LIVE_TRANSACTION",
            "data": event["data"]
        }))

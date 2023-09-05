from channels.generic.websocket import AsyncJsonWebsocketConsumer

class TokenAuthConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		await self.accept()
		print(self.scope["user"].username)
		print(self.scope["user"].email)
		print("Successfully connect In Backend!")
		self.send_json(
			{
				"message_response": "You are now connected to backend"
			})

	async def disconnect(self, close_code):
		print("Successfully Disconnect in backend!")

	async def receive_json(self, message):
		command = message.get("message")
		print(command)
		await self.send_json({
			"message_response": f"Responding: {command}"
		})

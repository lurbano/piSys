class websocketBroadcasterU:

	def __init__(self):
		self.clients = []

	def append(self, client):
		self.clients.append(client)

	def remove(self, client):
		self.clients.remove(client)

	def cast(self, whereTo, msg):
		message = {
			"info": whereTo,
			"msg": msg
		}
		for client in self.clients:
			client.write_message(message)

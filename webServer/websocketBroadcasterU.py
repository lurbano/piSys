class websocketBroadcasterU:

	def __init__(self):
		self.clients = []

	def cast(self, whereTo, msg):
		message = {
			"info": whereTo,
			"msg": msg
		}
		for client in self.clients:
			client.write_message(message)

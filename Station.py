class Station:
	def __init__(self,values):
		#Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs\n'
		self.MAC = values[0]
		self.Power = values[3]
		self.Packets = values[4]
	
	def getMAC(self):
		return self.MAC
		
	def getPower(self):
		return self.Power
		
	def getPackets(self):
		return self.Packets
		
	def toString(self):
		return (self.MAC +", "+self.Power+", "+self.Packets)

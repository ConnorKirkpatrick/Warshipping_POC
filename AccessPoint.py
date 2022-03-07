class AccessPoint:
	def __init__(self,values):
		#MAC, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key
		self.MAC = values[0]
		self.channel = str(int(values[3]))
		self.Security = values[5]
		self.Power = values[8]
		self.SSID = values[13]
		
	def getMAC(self):
		return self.MAC
		
	def getChannel(self):
		return self.channel
		
	def getSecurity(self):
		return self.Security
		
	def getPower(self):
		return self.Power
		
	def getSSID(self):
		return self.SSID
		
	def toString(self):
		return(self.MAC+", "+self.channel+", "+", "+self.Security+", "+ self.Power +", "+self.SSID)
		


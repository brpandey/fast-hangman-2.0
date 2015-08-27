from HangmanClock import HangmanClock

class HangmanDisplay:
	""""
	Class to handle display text modes wrt to game state and timing data
	"""

	_NONE, _SIMPLE, _NORMAL, _CHATTY = 0,1,2,3

	@property 
	def NONE(self): return HangmanDisplay._NONE
	@property 
	def SIMPLE(self): return HangmanDisplay._SIMPLE
	@property 
	def NORMAL(self): return HangmanDisplay._NORMAL
	@property 
	def CHATTY(self): return HangmanDisplay._CHATTY


	def __init__(self, verboselevel = _SIMPLE, clockflag = False):
		self._verboselevel = verboselevel

		if clockflag == True: 
			self._clock = HangmanClock()
		else:
			self._clock = None


	#Wrapper functions
	def bare(self, msg): self.__log(self.NONE, msg)
	def simple(self, msg): self.__log(self.SIMPLE, msg)
	def normal(self, msg): self.__log(self.NORMAL, msg)
	def chatty(self, msg): self.__log(self.CHATTY, msg)

	#Main logging function
	def __log(self, level, msg):
		if self._verboselevel >= level:
			
			if level == self.SIMPLE:
				print("{}".format(msg))

			elif level == self.NORMAL:
				print("[_] {}".format(msg))

			elif level == self.CHATTY:
				print("[H] {}".format(msg))

			elif level >= self.NONE:
				print("{}".format(msg))

	#Timing function that allows an output message
	def clock(self, msg):
		if self._clock != None: 
				self._clock.timer(msg)

	#User convenience functions
	def ischatty(self):
		if self._verboselevel >= self.CHATTY: return True
		else: return False



if __name__ == "__main__":
		display = HangmanDisplay(2, True)

		display.clock("Start time")
		display.simple("Here is a terse message")
		display.normal("Here is a normal message")
		display.chatty("Here is a verbose message")
		display.clock("End time")

		

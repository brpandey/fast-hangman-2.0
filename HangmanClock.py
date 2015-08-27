import time

class HangmanClock:
	"""
	Simple convenience class to handle timing
	"""


	def __init__(self):
		self._starttime = int(time.time() * 1000)
		self._lasttime = None
		self._counter = 1

	def timer(self, msg):
		"""
		Output method to capture timing info in milliseconds
	 	and also display clock comment given the clock level 
	 	is CLOCK. Clock information is output using the following format:
	 	[CLK][Counter][Now][Time Diff from Start][Time Diff from LastCalled]
		"""
		
		now = int(time.time() * 1000)

		if(self._lasttime == None):
			print("[CLK][{}][{}] {}".format(self._counter, now, msg))

		else:
			diff_from_start = now - self._starttime
			diff_from_last = now - self._lasttime

			print("[CLK][{}][{}][{}][{}] {}".format(self._counter, 
				now, diff_from_start, diff_from_last, msg))

		self._counter += 1
		self._lasttime = now

if __name__ == '__main__':
	clk = HangmanClock()
	clk.timer("test1")

	time.sleep(1)
	clk.timer('test2')

	time.sleep(2.4)
	clk.timer('test3')
		



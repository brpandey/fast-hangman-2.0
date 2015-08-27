import argparse

from HangmanDisplay import HangmanDisplay


class HangmanSettings:
	"""
	Process command line arguments for Hangman program
	and set various program modes, hangman words, clock levels, 
	display text modes, batch files and so forth.
	"""

	#game playing has a constant number of wrong guesses
	_MAX_WRONGGUESSES = 5

	_ERRORSCORE = -1

	_text_display = HangmanDisplay()

	_DISPLAYLEVELS = {'none':_text_display.NONE, \
			'simple':_text_display.SIMPLE, \
			'normal':_text_display.NORMAL, \
			'chatty':_text_display.CHATTY}

	_BASELINE = ['comaker','cumulate','eruptive', 'factual', 'monadism',
				'mus', 'nagging', 'oses', 'remembered', 'spodumenes',
				'stereoisomers','toxics','trichromats','triose', 'uniformed']

	def __argparse(self):
		parser = argparse.ArgumentParser(prog='Hangman', 
			description= 'Please enter a hangman word or specify a list of hangman words.\n ' \
			+ 'E.g. python PlayHangman.py -f words.txt -w ASTERISK')

		parser.add_argument('-f', dest='dictfile', required=True,
			nargs='?', type=argparse.FileType('r'), help='dictionary file name')

		parser.add_argument('-w', nargs='+', type=str, 
			dest='secrets', help='specify hangman word(s)')

		parser.add_argument('-display', help='output display verbosity level', 
			dest='display_type', type=str, default='none',
			choices=['simple', 'normal', 'chatty'])

		parser.add_argument('-clk', '--clock', 
			dest='clockflag', action='store_true', help='enable timing output')

		parser.add_argument('-bl', '--baseline', dest='baseline', action='store_const',
			const=HangmanSettings._BASELINE, help='run hangman against pre-specified baseline')

		parser.add_argument('--batch', dest='batchfile',
			nargs='?', type=argparse.FileType('r'), 
			help='batch hangmans file name')

		return parser.parse_args()


	def __init__(self):
		args = self.__argparse()

		self._dictfile = args.dictfile

		if args.secrets == None:
			self._secrets = ["avocado"]
		else:
			self._secrets = args.secrets
		
		if(HangmanSettings._DISPLAYLEVELS.get(args.display_type) == \
			HangmanSettings._DISPLAYLEVELS['none'] and args.baseline == None):
			self._verboselevel = HangmanSettings._DISPLAYLEVELS['simple']
		else:
			self._verboselevel = \
				HangmanSettings._DISPLAYLEVELS[args.display_type]

		if args.clockflag:
			self._clockflag = args.clockflag
		else:
			self._clockflag = False

		if args.batchfile:
			self._batchfile = args.batchfile
		else:
			self._batchfile = None

		if args.baseline:
			self._secrets = args.baseline

		self._display = HangmanDisplay(self._verboselevel, self._clockflag)

	#convenience function for engine
	def get_dictfile_name(self): return self._dictfile.name

	def get_dictfile_words(self, length):
		"""
		Generator function to read each word (line) from dictionary file
		"""

		try:
			if self._dictfile.closed: 
				self._dictfile = open(self._dictfile.name)

			with self._dictfile as fd:
				for wordline in fd:
					word = wordline.strip().lower()

					if(len(word) == length): 
						yield word

		except IOError as e:
			print 'gd Operation failed: %s' % e



	def get_secrets(self):
		"""
		Generator function that returns a secret hangman word at a time
		either from a list of secrets or batch file of secrets 
		"""

		if self._batchfile == None:
			for secret in self._secrets:
				yield secret.lower()

		else:
			try:
				with self._batchfile as file:
					for wordline in file:
						yield wordline.strip().lower()

			except IOError as e:
				print 'Operation failed: %s' % e

	@property
	def display(self):
		return self._display

	@property
	def max_incorrect(self):
		return self.__class__._MAX_WRONGGUESSES

	@property
	def errorscore(self):
		return self.__class__._ERRORSCORE

	def inspect(self):

		pstr = "HangmanSettings, dictfile {}, secrets {}," + \
			" verbosity {}, clock {}, batch {}"

		print(pstr.format(self._dictfile, \
				self._secrets, self._verboselevel, 
				self._clockflag, self._batchfile))


if __name__ == "__main__":
	settings = HangmanSettings()
	settings.inspect()

	for secret in settings.get_secrets():
		print("secret is: " + secret)

	cnt = 0

	for word in settings.get_dict_words():
		print("word is: " + word)

		if cnt == 10: break
		cnt += 1

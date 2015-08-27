class HangmanGame:

	#Constants representing current state of the game
	_STATUS_GAMEWON = 0
	_STATUS_GAMELOST = 1
	_STATUS_KEEPGUESSING = 2

	_STATUS = {0:'GAME_WON', 1:'GAME_LOST', 2:'KEEP_GUESSING'}

	#A marker for the letters in the secret words that have not
	#been guessed yet
	_MYSTERY_LETTER = '-'


	def __init__(self, secret_word, max_wrong_guesses):

		#The word that needs to be guessed
		self._secret_word = secret_word.upper()
		
		#The maximum number of wrong letter/word guesses that are allowed (e.g. 6, and if you exceed 6 then you lose)
		self._max_wrong_guesses = max_wrong_guesses
		
		#The letters guessed so far (unknown letters will be marked by the MYSTERY_LETTER constant). 
		self._guessed_so_far = []
		
		#Set of all correct letter guesses so far (e.g. 'A', 'M', 'C',
		self._correctly_guessed_letters = set()
		
		#Set of all incorrect letter guesses so far (e.g. 'X', 'B')
		self._incorrectly_guessed_letters = set()

		#Set of all incorrect word guesses so far 
		self._incorrectly_guessed_words = set()

		for i in range(len(secret_word)):
			self._guessed_so_far.append(HangmanGame._MYSTERY_LETTER)



	def guess_letter(self, letter):
		"""
		Guess the specified letter and update the game state accordingly

			Args:
				letter (str) the letter to guess
			Returns:
				the string representation of the current game state
				(which will contain MYSTERY_LETTER in place of unknown
				letters)

			Raises:
		"""
		self.assert_can_keep_guessing()
		
		letter = letter.upper()
		good_guess = False

		for i in range(len(self._secret_word)):
			if(self._secret_word[i] == letter):
				self._guessed_so_far[i] = letter
				good_guess = True

		if good_guess:
			self._correctly_guessed_letters.add(letter)
		else:
			self._incorrectly_guessed_letters.add(letter)

		return self.get_guessed_so_far()

	def guess_word(self, word):
		"""
		Guess the specified word and update the game state accordingly

			Args:
				word (str) the letter to guess
			Returns:
				the string representation of the current game state
				(which will contain MYSTERY_LETTER in place of unknown
				letters)

			Raises:
		"""
		self.assert_can_keep_guessing()

		word = word.upper()

		if word == self._secret_word:
			for i in range(len(self._secret_word)):
				self._guessed_so_far[i] = self._secret_word[i]

		else:
			self._incorrectly_guessed_words.add(word)

		return self.get_guessed_so_far()

	def current_score(self):
		"""
		Returns: The score for the current game state
		"""

		if self.game_status() == HangmanGame._STATUS_GAMELOST:
			return 25
		else:
			return self.num_wrong_guesses_made() + \
				len(self._correctly_guessed_letters)

	def assert_can_keep_guessing(self):
		if self.game_status() != HangmanGame._STATUS_KEEPGUESSING:
			raise Exception("IllegalStateException: " \
				+ "Cannot keep guessing in current game state " \
				+ "{}".format(self.game_status()))

	def game_status(self):
		"""
		Returns: The current game status
		"""
		if self._secret_word == self.get_guessed_so_far():
			return HangmanGame._STATUS_GAMEWON
		elif self.num_wrong_guesses_made() > self._max_wrong_guesses:
			return HangmanGame._STATUS_GAMELOST
		else:
			return HangmanGame._STATUS_KEEPGUESSING

	def num_wrong_guesses_made(self):
		"""
		Returns: Number of wrong guesses made so far
		"""
		return len(self._incorrectly_guessed_letters) \
			+ len(self._incorrectly_guessed_words)

	def num_wrong_guesses_remaining(self):
		"""
		Returns: Number of wrong guesses still allowed
		"""
		return self.get_max_wrong_guesses() - self.num_wrong_guesses_made()

	def get_max_wrong_guesses(self):
		"""
		Returns: Number of wrong guesses allowed
		"""
		return self._max_wrong_guesses

	def get_guessed_so_far(self):
		"""
		Returns: The string representation of the current game state \
		(which will contain MYSTERY_LETTER in place of unknown letters)
		"""
		return str("".join(self._guessed_so_far))

	def get_correctly_guessed_letters(self):
		"""
		Returns: Set of all correctly guessed letters so far
		"""
		return frozenset(self._correctly_guessed_letters)

	def get_incorrectly_guessed_letters(self):
		"""
		Returns: Set of all incorrectly guessed letters so far
		"""
		return frozenset(self._incorrectly_guessed_letters)

	def get_all_guessed_letters(self):
		"""
		Returns: Set of all guessed letters so far
		"""
		guessed = set()
		guessed.update(self._correctly_guessed_letters)
		guessed.update(self._incorrectly_guessed_letters)
		return guessed

	def get_incorrectly_guessed_words(self):
		"""
		Returns: Set of all incorrectly guessed words so far
		"""
		return frozenset(self._incorrectly_guessed_words)

	def get_secret_word_length(self):
		"""
		Returns: The length of the secret word
		"""
		return len(self._secret_word)


	def __str__(self):
		str = "{}; score={}; status={}".format(self.get_guessed_so_far(), \
			self.current_score(), self._STATUS[self.game_status()])
		return str

	@property
	def status_keep_guessing(self):
		return HangmanGame._STATUS_KEEPGUESSING

	@property
	def mystery_letter(self):
		return HangmanGame._MYSTERY_LETTER




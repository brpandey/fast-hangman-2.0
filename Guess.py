class Guess:
	"""
		Common interface for guessing.
	"""
	def __init__(self, guess):
		self._guess = guess

	def make_guess(self, game):
		raise Exception("Shouldn't be here")


class GuessLetter(Guess):
	"""
		A Guess that represents guessing a letter for the 
		current Hangman game
	"""

	def __init__(self, guess):
		Guess.__init__(self, guess)

	def make_guess(self, game):
		game.guess_letter(self._guess)

	def __str__(self):
		return "GuessLetter[" + self._guess + "]"

class GuessWord(Guess):
	"""
		A Guess that represents guessing a word for the 
		current Hangman game
	"""

	def __init__(self, guess):
		Guess.__init__(self, guess)

	def make_guess(self, game):
		game.guess_word(self._guess)

	def __str__(self):
		return "GuessWord[" + self._guess + "]"


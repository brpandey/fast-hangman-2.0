from HangmanGame import HangmanGame
from HangmanLetterStrategy import HangmanLetterStrategy
from HangmanSettings import HangmanSettings

class Hangman:
	"""
	Abstraction to represent a real hangman game that can be played (is playable)
	"""


	def __init__(self, settings):
		self._settings = settings
		self._display = settings.display


	def play(self, secret, maxincorrect):
		"""
		Play this hangman by setting up,
		then running the game with the strategy. Returns the score
	
		Args:
			self
			secret - the secret hangman word
			maxincorrect - the number of maximal wrong guesses

		Returns:
			score - game score
		"""
		
		game, strategy = self.__setup(secret, maxincorrect)
		self.__run(game, strategy)
		score = game.current_score()

		return score
		
	def __setup(self, secret, maxincorrect):
		"""
		(Private method)
		Setup the Hangman by setting up a Game object and a Strategy object
	
		Args:
			self
			secret - the secret hangman word
			maxincorrect - the number of maximal wrong guesses

		Returns:
			game - HangmanGame
			strategy - HangmanStrategy
		"""

		self._display.normal("(SHHH!!) hangman secret: {}\n".format(secret))
		
		game = HangmanGame(secret, maxincorrect)
				
		strategy = HangmanLetterStrategy(game, self._settings)
		
		return game, strategy

	def __run(self, game, strategy):
		"""
		(Private method)
		Runs the hangman game.  While game is not finished, keep guessing (playing)
		"""

		while game.game_status() == game.status_keep_guessing:
			
			guess, error = strategy.next_guess(game)

			if guess == None and error != None:
				self._display.simple("Aborting current game... [{}]".format(error))
				break
			
			guess.make_guess(game)

			self._display.simple(game)
			self._display.simple("")
			self._display.simple("")


if __name__ == '__main__':

	settings = HangmanSettings()
	display = settings.display
	max_incorrect = settings.max_incorrect

	secret = "asterisk"

	hangman = Hangman(settings)
	score = hangman.play(secret, max_incorrect)
		

	display.simple("Hangman.py: Given secret {}, score is {}".format(secret, score))



from HangmanSettings import HangmanSettings
from Hangman import Hangman
from HangmanWordPassEngine import HangmanWordPassEngine


if __name__ == '__main__':
	"""
	Driver code to play hangman either once or a sequence of games 
	as determined by the user settings 
	"""

	# Gather the settings info
	settings = HangmanSettings()
	display = settings.display
	max_incorrect = settings.max_incorrect
	count = 0
	total = 0

	display.clock("Start time")

	HangmanWordPassEngine.initialize(settings)

	# Grab the given secret from the generator function to start the game play!
	# No more secrets, no more play
	for secret in settings.get_secrets():

		hangman = Hangman(settings)
		
		score = hangman.play(secret, max_incorrect)
		total += score
		count += 1

		display.bare("{}: {}\n".format(secret.upper(), score))

		#display.clock("Finished game\n")


	# Compute the average score
	avg = float(total) / float(count)

	display.clock("End time")

	HangmanWordPassEngine.cleanup()

	if count > 1: display.bare("Given {} words, average word score is {}".format(count, avg))

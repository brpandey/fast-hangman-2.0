import re
from collections import Counter
from random import randint

from HangmanWordPassEngine import HangmanWordPassEngine
from Guess import GuessLetter
from Guess import GuessWord


class HangmanLetterStrategy:

	"""
	Abstraction to represent letter strategy component of game play.  
	HangmanLetterStrategy relies on HangmanWordPassEngine
	to perform its frequency count tally bookkeeping.  Strategy "calculations" 
	are dispatched to this module to find the best next letter guess 

	"""

		
	_english_lang_relative_letterfreq = \
		{'a':8.167, 'b':1.492, 'c':2.782, 'd':4.253, 'e':12.702, 
		 'f':2.228, 'g':2.015, 'h':6.094, 'i':6.966, 'j':0.153,
		 'k':0.772, 'l':4.025, 'm':2.406, 'n':6.749, 'o':7.507,
		 'p':1.929, 'q':0.095, 'r':5.987, 's':6.327, 't':9.056,
		 'u':2.758, 'v':0.978, 'w':2.360, 'x':0.150, 'y':1.974,
		 'z':0.074}
	

	_word_set_size = {'micro':2, 'tiny':5, 'small':9, 'large':550}

	_top_threshhold = 2

	def __init__(self, game, settings):
		"""
		Initialize the strategy given the length of the secret hangman word 
		"""

		self._mystery_letter = game.mystery_letter

		self._display = settings.display
		self.num_wrong_guesses_remaining = settings.max_incorrect
		self._last_guess = None

		self._letter_counts = Counter()
		self._guessed_letters = set()

		#This will be properly initialized when the tally function is called
		self._current_pass_size = 0

		self._last_word = None
		self._guessed_last_word = False

		#Initialize the HangmanWordPassEngine with the secret word length
		self._engine = HangmanWordPassEngine(game.get_secret_word_length(), \
				settings, self._mystery_letter)

		self._engine.setup(self)


	def __del__(self):

		self._guessed_letters.clear()
		self._guessed_letters = None

		self._letter_counts.clear()
		self._letter_counts = None


	def next_guess(self, game):
		"""
		Update game state and retrieve best possible next guess
		Sets up state for next game pass 
	
		Args:
			self
			game - instance of HangmanGame

		Returns:
			guess - either GuessLetter or GuessWord
			error - any particular error info
		"""
		assert(game != None)

		guess, error = None, None

		repat = None

		#We've had one guess already -- update engine state with this info before choosing next guess
		if game.current_score() > 0:  

			hangman_pattern = game.get_guessed_so_far().lower()
			last_guess_correct = self.__check_last_guess(game)

			# Create a counter object for current state of correct hangman letters
			# Make sure we don't track mystery display letters
			hangman_tally = Counter(hangman_pattern)
			del hangman_tally[self._mystery_letter]

			exclude_str = ''.join(str(x) for x in self._guessed_letters)

			# For each mystery_letter replace it with [^characters already guessed]
			repat = '^' + hangman_pattern.replace(self._mystery_letter, '[^' + exclude_str + ']') + "$"

			regex = re.compile(repat)
	
			#if the last guess was a letter, update the engine state accordingly
			if len(self._last_guess) == 1:

				pass_params_tuple_vector = (last_guess_correct, self._last_guess, \
					hangman_pattern, hangman_tally, regex, self._guessed_letters)

				self._engine.set_pass_params(pass_params_tuple_vector)

				tally, pass_size, self._last_word = self._engine.reduce()

				self.set_letter_counts(pass_size, tally)

		if self._display.ischatty():
			guessed = game.get_guessed_so_far()
			self._display.chatty("All guessed letters so far are {}".format(guessed))
			#self._display.chatty('regex pattern: {}'.format(repat))


		pass_size = self._current_pass_size

		if pass_size == 0: 
			error = "Game over, exhausted all words, word not in dictionary"
			#raise Exception("Word not in dictionary")

		elif pass_size == 1:
			if self._guessed_last_word != True:
				word = self._last_word
				guess = GuessWord(word)
				self._last_guess = word
				self._guessed_last_word = True
			else: 
				error = "Game over, exhausted all words, word not in dictionary"


		# most of the game play is where the pass size hasn't dwindled down to 0 or 1
		else:
			tally = self._letter_counts
			letter = self.__get_letter(tally, pass_size)

			if self._display.ischatty():
				self._display.chatty("letter counts are {}".format(tally))
				self._display.chatty("guess character is {}".format(letter))

			if letter != None:
				guess = GuessLetter(letter)
				self._guessed_letters.add(letter)
				self._last_guess = letter
			else:
				raise Exception("Unable to determine next guess")

		self._display.normal(guess)
		
		return guess, error

	def __check_last_guess(self, game):
		"""
		Helper function to check if the last guess was correct or not
		"""

		remaining_count = game.num_wrong_guesses_remaining()

		if self.num_wrong_guesses_remaining == remaining_count:
			flag = True
			self._display.chatty("<Correct guess>")

		else:
			#otherwise we need to update the remaining count 
			#because it has changed due to a incorrect guess
			self.num_wrong_guesses_remaining = remaining_count
			flag = False
			self._display.chatty("<Wrong guess>")

		return flag


	def __get_letter(self, tally, pass_size):
		"""
		Retrieve the next letter to guess 
	
		Args:
			self
			tally - a dict of the letter, frequency counts
			pass_size -  number of words in word set 

		Returns:
			letter - best letter
		"""

		assert(sum(tally.values()) > 0 and pass_size > 1)

		letter, count = self.__strategic_letter_most_common_hybrid(tally, pass_size)

		msg = "letter is {}, counts is {}, pass_size is {}"
		self._display.chatty(msg.format(letter, count, pass_size))

		return letter


	def __strategic_letter_most_common(self, tally, pass_size):
		"""
		Most common letter retrieval strategy.  
		Get the first letter with the highest frequency in the possible hangman word set.
		Doesn't handle tie's between letters.

		Args:
			self
			tally - a dict of the letter, frequency counts
			pass_size -  number of words in word set 

		Returns:
			letter - best letter
			count - letter frequency count
		"""

		assert(sum(tally.values()) > 0 and pass_size > 1)

		list = tally.most_common(1)

		letter, count = list[0]
	
		return letter, count

	def __strategic_letter_most_common_hybrid(self, tally, pass_size):
		"""
		Most common letter retrieval strategy with a twist.  
		Get the first letter with the highest frequency for when the current possible 
		hangman word set space is > "small".  Add a twist and combine english lang letter
		relative frequency.

		For the cases where the word set is less than small, 
		only take the letter whose frequencies are less than or equal half the possible hangman word set size.  
		E.g. for size 10, letter counts would need to be 5 or lower to be chosen

		Doesn't handle tie's between letters.


		Args:
			self
			tally - a dict of the letter, frequency counts
			pass_size -  number of words in word set 

		Returns:
			letter - best letter
			count - letter frequency count
		"""

		assert(sum(tally.values()) > 0 and pass_size > 1)

		letter, count = None, None

		if pass_size > HangmanLetterStrategy._word_set_size['small']:

			list = tally.most_common(3)

			letter, count = list[0]

			letter_2, count_2 = list[1]

			# Add a twist and combine english lang letter relative frequency!
			#if count_2 >= pass_size/2: 

			x1 = (1 + HangmanLetterStrategy._english_lang_relative_letterfreq[letter])*count

			x2 = (1 + HangmanLetterStrategy._english_lang_relative_letterfreq[letter_2])*count_2

			if x2 > x1: 
				letter, count = letter_2, count_2

			#self._display.chatty('x1 {} x2 {}, choosing letter {} count {}'.format(x1, x2, letter, count))
		
		
		else:
			#take out those elements from tally where the letter
			#count is greater than half the bucket size
			
			list = [(k,v) for (k,v) in tally.items() if v <= pass_size/2 ]

			if len(list) == 0: list = [(k,v) for (k,v) in tally.items()]

			common = Counter(dict(list)).most_common(1)

			letter, count = common[0]
		
			
		return letter, count


	def __strategic_letter_closest_half(self, tally, pass_size):
		"""
		Choose the letter based on letter frequency count that is closest to half the 
		current possible hangman word set size 

		Doesn't handle tie's between letters.

		Args:
			self
			tally - a dict of the letter, frequency counts
			pass_size -  number of words in word set 

		Returns:
			letter - best letter
			count - letter frequency count
		"""
		assert(sum(tally.values()) > 0 and pass_size > 1)

		closest = Counter(dict([(a,abs(b-pass_size/2)) \
			for (a,b) in tally.items()]))

		list = closest.most_common()[:-2:-1]

		letter, count = list[0]
			
		return letter, count

	def set_letter_counts(self, pass_size, letter_counts):

		self._current_pass_size = pass_size
		self._letter_counts.clear()
		self._letter_counts += letter_counts

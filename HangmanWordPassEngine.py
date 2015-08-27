import copy
import itertools
import os

from collections import Counter

"""
The facts:
174k words ~ in words.txt

awk '{print length}' words.txt | sort -n | uniq -c
// words length
	  96 2
	 978 3
	3919 4
	8672 5
	15290 6
	23208 7
	28558 8
	25011 9
	20404 10
	15581 11
	11382 12
	7835 13
	5134 14
	3198 15
	1938 16
	1125 17
	 594 18
	 328 19
	 159 20
	  62 21
	  29 22
	  13 23
	   9 24
	   2 25
	   2 27
	   1 28

"""


class HangmanWordPassEngine:
	"""	
	Performs general bookkeeping of current possible hangman word set space.  
	Provides techniques to prune word set space given
	a correctly or incorrectly guessed letter along with other parameters. 
	Manages intermediate pass data

	Used exclusively by HangmanLetterStrategy.
	"""

	#This dict contains the counts of all the characters in each of 
	#the word length arranged word sets
	_letter_counters = {}
	_static_initalized = False
	_sorted_dictfile = None
	_passfile_A = None	
	_passfile_B = None
	_unchanging_randval = '234902358039284234832893842'



	def __init__(self, answer_length, settings, mystery_letter):

		self._settings = settings
		self._display = settings.display		
		self._answer_length = answer_length
		self._mystery_letter = mystery_letter
		self._current_words_pipeline_readable = None
		self._current_pass = 1
		#self._regex_used = 0

		self.__initialize_passfiles()


	def __del__(self):

		self._answer_length = None
		self._display = None
		self._settings = None
		self._current_words_pipeline_readable = None
		self._current_write_passfile = None
		self._current_read_passfile = None
		self._previous_write_passfile = None
		self._passfile_cycle = None


	@staticmethod
	def cleanup():
		try:
			if HangmanWordPassEngine._sorted_dictfile != None:
				os.remove(HangmanWordPassEngine._sorted_dictfile.name)
			if HangmanWordPassEngine._passfile_A != None: 
				os.remove(HangmanWordPassEngine._passfile_A.name)
			if HangmanWordPassEngine._passfile_B != None: 
				os.remove(HangmanWordPassEngine._passfile_B.name)
			
			HangmanWordPassEngine._sorted_dictfile = None
			HangmanWordPassEngine._passfile_A = None
			HangmanWordPassEngine._passfile_B = None

			HangmanWordPassEngine._letter_counters.clear()
			HangmanWordPassEngine._letter_counters = None
		except OSError as e:
			print 'Operation failed: %s' % e

	@staticmethod
	def initialize(settings):
		
		if HangmanWordPassEngine._static_initalized == False:

			settings.display.clock("Statically Initializing engine 0.1")
			HangmanWordPassEngine.__sort_and_write_dictfile_words(settings)
			
			settings.display.clock("Statically Initializing engine 0.2")


		HangmanWordPassEngine._static_initalized = True


	def setup(self, letter_strategy):
		"""
		Setup the engine. Initialize word set and counter structures to accurately
			reflect current word set and tally data
		Args: self, strategy
		Returns: Nothing
		"""

		self._display.chatty("Entering setup")

		counter = None

		# access class static _letter_counters dict for cached copy of counter
		counter_tuple = HangmanWordPassEngine._letter_counters.get(self._answer_length)

		if counter_tuple != None: pass_size, counter = counter_tuple


		if counter != None:
			letter_strategy.set_letter_counts(pass_size, copy.deepcopy(counter))
					
			# Set first pass of dictionary words
		
			# grab the words from the sorted dictionary file using the get_dictfile_words generator
			file_pass_A = (word for word in HangmanWordPassEngine.__get_grouped_words(self._answer_length))
			
			self._current_words_pipeline_readable = file_pass_A
		
		else:
			# Second pass of dictionary words
			# tally all the dictionary words and store for later

			#file_pass_B = (word for word in self._settings.get_dictfile_words(self._answer_length))
			file_pass_B = (word for word in HangmanWordPassEngine.__get_grouped_words(self._answer_length))

			tally, pass_size, _ = self.__process_and_tally_filtered_generator(set(), file_pass_B)

			letter_strategy.set_letter_counts(pass_size, tally)

			counts_deepcpy = copy.deepcopy(tally)

			HangmanWordPassEngine._letter_counters[self._answer_length] = (pass_size, counts_deepcpy)

		self._display.chatty("Finished setup")

	#helper routine
	def __initialize_passfiles(self):

		try:
			#make the log name hard to guess
			id = HangmanWordPassEngine._unchanging_randval 

			if HangmanWordPassEngine._passfile_A == None and \
				HangmanWordPassEngine._passfile_B == None:
				
				# setup appropriate file streams for pass files
				HangmanWordPassEngine._passfile_A = open("passfile_" + id + "_A.log", 'w')
				HangmanWordPassEngine._passfile_B = open("passfile_" + id + "_B.log", 'w')

			passfile_sequence = [HangmanWordPassEngine._passfile_A, HangmanWordPassEngine._passfile_B]
			
			# cycle between files for reading and writing
			self._passfile_cycle = itertools.cycle(passfile_sequence)
			self._current_write_passfile = None

		except IOError as e:
			print 'Operation failed: %s' % e



	def set_pass_params(self, pass_params_tuple_vector):
		''''
		set_pass_params
		Input tuple vector should be of following format
		filter_params_tuple = (last_guess_correct, letter, hangman_pattern, hangman_tally, regex, exclusion)

		'input' vector in used to reduce the word space

		last_guess_correct - last guess state (either correct or incorrect)
		letter - the letter to reduce the word set space from
		hangman_pattern - current hangman letter pattern state sequence
		hangman_tally - counter of letters in hangman pattern w/o mystery letter
		regex - compile regex object created from hangman_pattern
		exclusion - exclusion set of letters already guessed
		'''

		self._current_filter_pass_params = pass_params_tuple_vector


	def reduce(self):
		"""
		Reduce the word set space,	update the unique map of letter/counts 
		given the new word set universe
	
		Returns tuple w/ updated state 
		"""

		last_guess_correct, guess, hangman_pattern, hangman_tally, regex, exclusion \
			 = self._current_filter_pass_params

		assert(last_guess_correct != None and guess != None and exclusion != None \
			and hangman_pattern != None and hangman_tally != None and regex != None)

		if last_guess_correct: 
			updated_state_tuple = self.__filter_correct_guess()
		else: 	
			updated_state_tuple = self.__filter_wrong_guess()

		return updated_state_tuple


	def __possible_hangman_words(self):
		"""
		Generator function to iterate through the current word pass sequence
		"""

		while True:
			try:
				words_iter = iter(self._current_words_pipeline_readable)
				word = words_iter.next()

				yield word
			except StopIteration:
				break;


	def __process_and_tally_filtered_generator(self, exclusion, (filtered_generator)):
		"""
		Store the filtered word pass generator and tally the words while its being written to file.  
		"""

		assert(filtered_generator != None)

		#write to the pass file
		updated_state_tuple = self.__write_and_tally_passfile(exclusion, filtered_generator)

		# store generator of file
		# grab the words from the recently output passfile using the read_passfile_words generator
		self._current_words_pipeline_readable = (word for word in self.__read_passfile_words())

		return updated_state_tuple



	def __filter_wrong_guess(self):
		"""
		Reduce the word set space, 
		knowing that words containing 'letter' are candidates for removal
	
		Args:
			self
			letter - the incorrect letter to reduce the word set space from
		Returns:
			Nothing
		"""

		_, wrong_letter, _, _, _, exclusion  = self._current_filter_pass_params

		#generator comprehension to generate all words that don't have the letter
		#store the filtered pass
		words_filtered_pass = (word for word in self.__possible_hangman_words() if word.find(wrong_letter) == -1)

		updated_state_tuple = self.__process_and_tally_filtered_generator(exclusion, words_filtered_pass)

		return updated_state_tuple

	def __filter_correct_guess(self):
		"""
		Reduce the word set space, using a generator
		Returns: Nothing
		"""

		words_filtered_pass = itertools.ifilter(None, \
				itertools.imap(self.__filter_candidate_word_regex, self.__possible_hangman_words()))


		_, _, _, _, _, exclusion  = self._current_filter_pass_params

		updated_state_tuple = self.__process_and_tally_filtered_generator(exclusion, words_filtered_pass)

		return updated_state_tuple


	def __filter_candidate_word_regex(self, word):
		
		_, _, _, _, regex, _  = self._current_filter_pass_params

		if regex.match(word) == None: return False

		return word
		


	def __filter_candidate_word(self, word):
		"""
		Reduce the word set space: 
			a) knowing words not containing 'letter' are candidates for removal
			b) words that don't have the same letter counts for 'letter' are candidates
			c) words whose positions for 'letter' don't match are candidates
		"""

		_, correct_letter, hangman_pattern, hangman_tally, _, _  = self._current_filter_pass_params

		assert(word != None  and correct_letter != None and hangman_tally != None)

		#if the correct letter is not found in the word, it can't be a candidate
		if word.find(correct_letter) == -1: return False;

		#if the correct hangman pattern letter counts don't match those of the word, it can't be a candidate
		if self.__check_letter_counts_match(word, hangman_tally) == False: return False;

		#if the correct hangman pattern letter positions don't match those of the word, it can't be a candidate
		if self.__check_letter_positions_match(word, hangman_pattern) == False: return False;

		#print 'HangmanWordPassEngine - filter candidate word - matches!!!', word

		return word;


	def __check_letter_counts_match(self, word, hangman_tally):
		"""
		Ensure the known letter counts, in the given word, match the letter counts in the tally
	
		Args:
			self
			word - given dictionary word
			hangman_tally - tally of the known letter counts to check against

		Returns:
			boolean - True or False
		"""

		assert(word != None and hangman_tally != None)

		tally = copy.deepcopy(hangman_tally)

		processed = set()

		#iterate through the characters in the word
		for i in range(len(word)):
			letter = word[i]

			#Only care if the letter is in the counter
			#Or has already been processed as having been in the counter
			if tally[letter] != 0 or letter in processed: 
				tally[letter] -= 1
				processed.add(letter)

		if sum(tally.values()) != 0: 
			return False

		return True


	def __check_letter_positions_match(self, word, hangman_pattern):
		"""
		Ensure the known letter positions in the hangman word match those in the given word
	
		Args:
			self
			word - given dictionary word
			hangman - hangman secret word

		Returns:
			boolean - True or False
		"""

		assert(word != None and hangman_pattern != None)

		for i in range(len(hangman_pattern)):

			if hangman_pattern[i] != self._mystery_letter and hangman_pattern[i] != word[i]:
				return False

		return True


	@staticmethod
	def __sort_and_write_dictfile_words(settings):
		"""
		Function to read and then sort lines from dictionary file
		Assuming the dictionary words are well formed words and unique

		"""

		try:
			#make the log name hard to guess
			id = HangmanWordPassEngine._unchanging_randval

			fdr = open(settings.get_dictfile_name())
			HangmanWordPassEngine._sorted_dictfile = open("words_sorted_" + id + ".txt",'w')

			lines = fdr.readlines()
			lines.sort(key=len)

			map(HangmanWordPassEngine._sorted_dictfile.write, lines)
			
			fdr.close()

			HangmanWordPassEngine._sorted_dictfile.close()

		except IOError as e:
			print 'Operation failed: %s' % e


	@staticmethod
	def __get_sorted_dictfile_words():
		"""
		Generator function to read each word (line) from sorted dictionary file
		"""
		
		#last_read_word = None

		try:
			if HangmanWordPassEngine._sorted_dictfile.closed: 
				HangmanWordPassEngine._sorted_dictfile =\
					open(HangmanWordPassEngine._sorted_dictfile.name)


			with HangmanWordPassEngine._sorted_dictfile as fd:
				for wordline in fd:
					word = wordline.strip().lower()

					#performance hit
					#nice to have but not necessary given well-formed dictionary assumption
					#since this is a sorted file we can easily skip duplicates just in case
					#if last_read_word != None and last_read_word == word: continue

					yield word

					#last_read_word = word


		except IOError as e:
			print 'gd Operation failed: %s' % e

	@staticmethod
	def __get_grouped_words(group_key):
		
		for key, igroup in \
			itertools.groupby(HangmanWordPassEngine.__get_sorted_dictfile_words(), lambda x: len(x)):
   			
   			if group_key == key: 
   				for word in igroup:
   					yield word

	
	def __read_passfile_words(self):
		"""
		Generator function to read each word (line) from dictionary file
		"""

		self._current_read_passfile = self._previous_write_passfile

		try:
			if self._current_read_passfile.closed: 
				self._current_read_passfile = open(self._current_read_passfile.name, 'r')

			with self._current_read_passfile as fd:
				for wordline in fd:
					word = wordline.strip()

					#self._display.chatty("read_passfile {}, word: {}".format(self._current_read_passfile, word))

					yield word

		except IOError as e:
			print 'rp Operation failed: %s' % e



	def __write_and_tally_passfile(self, exclusion, (words_generator)):
		"""
		Function to write each word from a generator to a pass file
		Tallies the generator words while they are being written (saving an extra file read)

		By "tally" - specifically, tally the unique word letters
		Given a word, tally the various letters in the word by uniqueness.  
	 	If there are two a's in a word record only 1 a.  If an exclusion set is 
	 	provided, ignore the letters found in the exclusion set e.g. already guessed letters.
		"""

		assert(exclusion != None and words_generator != None)

		tally = Counter()

		word_num = -1
		last_word = None

		self._current_write_passfile = next(self._passfile_cycle)

		try:
			if self._current_write_passfile.closed: 
				self._current_write_passfile = open(self._current_write_passfile.name, 'w')

				#self._display.clock("Deciding next guess 1.22")

			#self._display.clock("write and tally passfile 1.23")

			with self._current_write_passfile as fd:
				for word_num, word in enumerate(iter(words_generator)):

					#self._display.chatty("write_passfile {}, word: {}".format(self._current_write_passfile, word))

					fd.write("{}\n".format(word))

					#self._display.clock("write and tally passfile 1.24{}".format(word_num))


					processed = set()

					for i in range(len(word)):
						letter = word[i]
						
						if exclusion != None and letter in exclusion: 
							continue

						if letter not in processed:	
							tally[letter] += 1
							processed.add(letter)

				if word_num + 1 == 1: 
					last_word = word

			#self._display.clock("write and tally passfile 1.25")

		except IOError as e:
			print 'wtp Operation failed: %s' % e

		self._previous_write_passfile = self._current_write_passfile

		return (tally, word_num + 1, last_word)

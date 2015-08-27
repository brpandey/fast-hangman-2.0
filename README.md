Hangman written in Python 2.7

Uses functional style of programming (think itertools)
using python generators and pass files for each run.  Very fast too!

Example:

python PlayHangman.py -f words.txt -clk -w avocado
[CLK][1][1440657846194] Start time
[CLK][2][1440657846194][0][0] Statically Initializing engine 0.1
[CLK][3][1440657846405][211][211] Statically Initializing engine 0.2
-------; score=1; status=KEEP_GUESSING


A---A--; score=2; status=KEEP_GUESSING


A---A--; score=3; status=KEEP_GUESSING


A---A--; score=4; status=KEEP_GUESSING


A---A--; score=5; status=KEEP_GUESSING


A---AD-; score=6; status=KEEP_GUESSING


AVOCADO; score=6; status=GAME_WON


AVOCADO: 6
[CLK][4][1440657847096][902][691] End time



python PlayHangman.py -f words.txt -clk -bl
[CLK][1][1440657904363] Start time
[CLK][2][1440657904364][1][1] Statically Initializing engine 0.1
[CLK][3][1440657904575][212][211] Statically Initializing engine 0.2
COMAKER: 9
CUMULATE: 8
ERUPTIVE: 5
FACTUAL: 7
MONADISM: 7
MUS: 25
NAGGING: 7
OSES: 3
REMEMBERED: 4
SPODUMENES: 4
STEREOISOMERS: 3
TOXICS: 8
TRICHROMATS: 4
TRIOSE: 7
UNIFORMED: 6
[CLK][4][1440657911285][6922][6710] End time
Given 15 words, average word score is 7.13333333333




python PlayHangman.py -f words.txt -w eruptive
E------E; score=1; status=KEEP_GUESSING


E------E; score=2; status=KEEP_GUESSING


E----I-E; score=3; status=KEEP_GUESSING


E----I-E; score=4; status=KEEP_GUESSING


ER---I-E; score=5; status=KEEP_GUESSING


ERUPTIVE; score=5; status=GAME_WON


ERUPTIVE: 5





Usage:

$ python PlayHangman.py -h
usage: Hangman [-h] -f [DICTFILE] [-w SECRETS [SECRETS ...]]
               [-display {simple,normal,chatty,noisy,debug}] [-clk] [-bl]
               [--batch [BATCHFILE]]

Please enter a hangman word or specify a list of hangman words

optional arguments:
  -h, --help            show this help message and exit
  -f [DICTFILE]         dictionary file name
  -w SECRETS [SECRETS ...]
                        specify hangman word(s)
  -display {simple,normal,chatty,noisy,debug}
                        output display verbosity level
  -clk, --clock         enable timing output
  -bl, --baseline       run hangman against pre-specified baseline
  --batch [BATCHFILE]   batch hangmans file name

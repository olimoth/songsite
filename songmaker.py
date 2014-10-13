''' 
Nonsense song generator. Thought I was going to use a Directed Acyclic Word Graph
but realised it's not necessary and all I need is a reverse Trie to look up suffixes.
'''

import argparse
import collections
import datetime
import itertools
import logging
import math
import random
import re
import string
import StringIO
import sys
import unittest


LOWER_CASE_LETTERS = string.lowercase
VOWELS = 'aeiouy'
CONSONANTS = ''.join([l for l in LOWER_CASE_LETTERS if l not in VOWELS])


class TrieNode(object):
    ''' A Trie data structure. Collapses word prefixes '''

    def __init__(self, letter=None, is_word=False):
        self.letter = letter
        self.is_word = is_word
        self.children = {}

    def add_letters(self, letters):
        ''' Adds letters to this node '''
        child_exists = self.children.has_key(letters[0])
        if len(letters) > 1:
            if not child_exists:
                self.children[letters[0]] = TrieNode(letters[0])
            self.children[letters[0]].add_letters(letters[1:])
        else:
            if not child_exists:
                self.children[letters[0]] = TrieNode(letters[0], is_word=True)
            else:
                self.children[letters[0]].is_word = True

    def words_with_prefix(self, prefix, reverse=False):
        ''' Returns a list of words with a given prefix '''
        # read down trie until the end of the prefix
        current_child = self
        for letter in prefix:
            try:
                current_child = current_child.children[letter]
            except KeyError:
                return []
        all_words = current_child.get_all_words()
        # all words will have last letter of prefix already
        words_with_prefix = [prefix[:-1] + w for w in all_words]
        if reverse:
            words_with_prefix = [w[::-1] for w in words_with_prefix]
        return words_with_prefix

    def get_all_prefixes(self, num_syllables, reverse=False):
        ''' 
        Gets all prefixes with num_syllables in this trie. 
        Reverse means reverse the prefix before checking the syllable count
        in case this is a suffix-ordered trie.
        '''
        def prefix_matcher(node, word):
            if reverse:
                word = word[::-1]
            return count_syllables(word) == num_syllables
        return self.match_all(prefix_matcher, descend_on_match=False)

    def get_all_words(self, words=None, word_so_far=''):
        ''' Appends all the words contained in this trie to the passed-in list'''
        def word_matcher(node, word):
            return node.is_word
        return self.match_all(word_matcher, descend_on_match=True)

    def match_all(self, match_func, descend_on_match, matches=None, match_so_far=''):
        ''' 
        Searches the whole trie, returning all substrings that return true from match_func
        '''
        if matches == None:
            matches = []
        match_so_far += self.letter if self.letter else ''
        # we're at a leaf node, return
        if match_func(self, match_so_far) and len(self.children) == 0:
            matches.append(match_so_far)
        # there are children left, keep going
        for node in self.children.values():
            if match_func(self, match_so_far):
                matches.append(match_so_far)
                if not descend_on_match:
                    continue
            node.match_all(match_func, descend_on_match, matches, match_so_far)
        return set(matches)


def count_syllables(word):
    # find all groups of vowels followed by one or more consonants
    # todo: look backwards on word boundary and take all vowels. BOOYAH
    regex = r'[{vowels}]+(?=[{consonants}]*)'.format(
        vowels=VOWELS, consonants=CONSONANTS)
    vowel_groups = re.findall(regex, word)
    syllables = len(vowel_groups)
    # no vowels, fuck this!
    if syllables == 0:
        return 0
    # if the last vowel group is a single 'e', it's probably not a syllable
    # if it's a single other vowel or multiple vowels it probably is a syllable
    if vowel_groups[-1] == 'e' and word[-1] in VOWELS:
        syllables -= 1
    # count the double syllables and increase the syllable count for each
    doubles = ['ui', 'ia', 'ea', 'io']
    syllables += len([v for v in vowel_groups if v in doubles])
    return syllables



class Letter(object):
    ''' 
    Represents a letter, including how often it appears at a given position in a word
    and the frequency with which other letters follow it
    '''
    def __init__(self, letter):
        self.letter = letter
        self.positions = collections.defaultdict(int)
        self.followers = {}
        for letter in LOWER_CASE_LETTERS: 
            self.followers[letter] = 0

    def add_follower(self, follower):
        self.followers[follower] += 1

    def add_position(self, position):
        self.positions[position] += 1


class Reader(object):
    ''' 
    Reads text and extracts letter frequency information 
    '''
    def __init__(self, text):
        ''' text should be a file-like object '''
        self.text = text
        self.letters = {}
        for letter in LOWER_CASE_LETTERS: 
            self.letters[letter] = Letter(letter)

    def parse_text(self):
        for line in self.text:
            # lower and strip everything except letters
            line = line.lower()
            words = re.findall('[a-z]+', line)
            for word in words:
                for i, letter in enumerate(word):
                    if i+1 < len(word):
                        self.letters[letter].add_follower(word[i+1])
                    self.letters[letter].add_position(i)

    def letters_at_position(self, position, num_letters):
        ''' 
        Gets the top num_letters letters for a given position. 
        Returns list ordered by frequency
        '''
        all_positions = {}
        for letter in self.letters: 
            all_positions[letter] = self.letters[letter].positions[position]
        return sorted(all_positions, key=all_positions.get, reverse=True)[:num_letters]

    def specific_letters_at_position(self, position, letters):
        ''' Returns the same list as the input letters, but ordered by frequency at position'''
        letters_at_position = self.letters_at_position(position, 26)
        return [l for l in letters_at_position if l in letters]

    def following_letters(self, letter, num_letters):
        ''' Gets num_letters of the most frequent followers of letter '''
        followers = self.letters[letter].followers
        return sorted(followers, key=followers.get, reverse=True)[:num_letters]



class WordGenerator(object):
    ''' 
    Uses a Reader to extract letter frequency and position info from some
    text, and uses that to generate random but pronouceable words
    '''
    def __init__(self, reader, min_letters, max_letters, allow_doubles):
        self.reader = reader
        self.min_letters = min_letters
        self.max_letters = max_letters
        self.allow_doubles = allow_doubles
        self.start_letters = 18
        self.follower_count = 12
        self.position_limit = 6
        large_consonant_group_pattern = '[%s]{%s,}' % (CONSONANTS, 3)
        consonant_class = '[%s]+' % CONSONANTS
        invalid_start_patterns = ['mr', 'gn', 'hn', 'hr', 'rn', 'mn', 'nt', 'lt', 'nl', 'wn']
        invalid_start_regexes = [r'\b'+p+'+' for p in invalid_start_patterns]
        invalid_mid_patterns = ['br{c}', 'gn{c}', '{c}dl', '{c}lt', '{c}sl']
        invalid_mid_regexes = [p.format(c=consonant_class) for p in invalid_mid_patterns]
        invalid_end_patterns = ['tl', 'sl', 'dr', 'dl'] 
        invalid_end_regexes = [p+r'\b' for p in invalid_end_patterns]
        concatenated_reject_patterns = '|'.join((
            [large_consonant_group_pattern] +
            invalid_start_regexes + 
            invalid_mid_regexes + 
            invalid_end_regexes))
        logging.debug('combined reject regexes: %s' % concatenated_reject_patterns)
        self.reject_patterns = re.compile(concatenated_reject_patterns)

    def generate_word(self):
        word_length = random.randint(self.min_letters, self.max_letters)
        logging.debug('making a word %s letters long' % word_length)
        word = random.choice(self.reader.letters_at_position(0, self.start_letters))
        logging.debug('first letter is %s, chosen from %s' % (
            word, self.reader.letters_at_position(0, self.start_letters)))
        while len(word) < word_length:
            logging.debug('word is currently %s' % word)
            frequent_followers = self.reader.following_letters(word[-1], self.follower_count)
            logging.debug('frequent followers of %s are %s' % (word[-1], frequent_followers))
            if not self.allow_doubles:
                try:
                    frequent_followers.remove(word[-1]) # prevent doubles
                except ValueError:
                    pass
            most_likely_at_position = self.reader.specific_letters_at_position(
                position=len(word), letters=frequent_followers)[:self.position_limit]
            logging.debug('the letters most likely at this position are %s' % (
                most_likely_at_position))
            next_letter = random.choice(most_likely_at_position)
            # check for disallowed patterns
            if self.reject_patterns.search(word + next_letter):
                logging.debug('word "%s" failed' % (word + next_letter))
            else:
                word += next_letter 
        return word


class SongWriter(object):
    ''' 
    Uses a reverse Trie to write songs that rhyme by matching end syllables 
    '''
    def __init__(self, words):
        self.all_words = words
        self.words_by_syllable = None
        self.trie = None
        self.first_time = True

    def get_parsed_rhyming_scheme(self, rhyming_scheme):
        ''' 
        Rhyming scheme is of the form N:X, where N is number of syllables in the line
        and X is the type of rhyme. For example the rhyming scheme for a limerick is:
        8a,8a,5b,5b,8a
        Returns a list of tuples of the form [(syllables, rhyme), ...]
        '''
        split_regex = r'([0-9]+)([a-z]),?'
        lines = re.findall(split_regex, rhyming_scheme)
        return [(int(line[0]), line[1]) for line in lines]

    def get_words_by_syllable(self, words):
        words_by_syllable = collections.defaultdict(list)
        syllable_word_pairs = zip(map(count_syllables, words), words)
        for pair in syllable_word_pairs:
            words_by_syllable[pair[0]].append(pair[1])
        return words_by_syllable
    
    def get_rhyme_groups(self):
        all_prefixes = self.trie.get_all_prefixes(num_syllables=1, reverse=True)
        return [self.trie.words_with_prefix(p, reverse=True) for p in all_prefixes]

    def construct_maps(self):
        if not self.first_time:
            return
        self.first_time = False
        # fill up our trie with reversed words so we can search by suffix 
        self.trie = TrieNode()
        for word in self.all_words:
            self.trie.add_letters(word[::-1])
        # organise our words into a map of syllables-to-words
        self.words_by_syllable = self.get_words_by_syllable(self.all_words)
        # get all rhyme groups and sort them into word-by-syllable maps
        rhyme_groups = self.get_rhyme_groups()
        self.rhyme_groups = [self.get_words_by_syllable(g) for g in rhyme_groups]

    def get_song(self, rhyming_scheme, min_syllables=1, max_syllables=4):
        ''' Get a random song based on the words contained in self.trie '''
        # check if min < 0 or max > [word group with highest number of syllables]
        # and return error (throw exception?)
        self.construct_maps()
        scheme = self.get_parsed_rhyming_scheme(rhyming_scheme)
        distinct_schemes = set([line[1] for line in scheme])
        scheme_to_words = {}
        # make a copy so we can remove entries to avoid duplicate rhymes, 
        # but keep the original map around for future songs
        rhyme_group_copy = list(self.rhyme_groups)
        for distinct_scheme in distinct_schemes:
            assert(len(self.rhyme_groups) > 1)
            rhyme_group = random.choice(rhyme_group_copy)
            scheme_to_words[distinct_scheme] = rhyme_group
            rhyme_group_copy.remove(rhyme_group)
        song = []
        for current_line_scheme in scheme:
            line = ''
            current_line_syllables = 0
            last_word_max_syllables = random.randint(min_syllables, max_syllables) 
            while current_line_syllables < current_line_scheme[0] - last_word_max_syllables:
                current_word_syllables = random.randint(min_syllables, max_syllables) 
                current_word = random.choice(self.words_by_syllable[current_word_syllables])
                line += current_word + ' '
                current_line_syllables += current_word_syllables
            # finish line with word of remaining syllables from chosen rhyme group
            rhyme_word_syllables = current_line_scheme[0] - current_line_syllables
            rhyme_word = random.choice(
                scheme_to_words[current_line_scheme[1]][rhyme_word_syllables])
            line += rhyme_word
            song.append(line)
        return song


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Activate debug logging')
    parser.add_argument('--source-text', default='eightydays.txt',
        help='The source text to extract letter frequency data from')
    parser.add_argument('--min', type=int, default=4, 
        help='Minimum number of letters in words')
    parser.add_argument('--max', type=int, default=9, 
        help='Maximum number of letters in words')
    parser.add_argument('-w', '--generate-words', action='store_true')
    parser.add_argument('-s', '--generate-songs', action='store_true')
    parser.add_argument('-p', '--rhyming-scheme', default='8a,8a,5b,5b,8a',
        help='The rhyming scheme of the song. Defaults to limericks')
    parser.add_argument('-n', '--num-words', type=int, default=50000,
        help='Number of words to add to song pool')
    parser.add_argument('--allow-doubles', action='store_true', help='Allow double letters')
    parser.add_argument('--benchmark', type=int, help='Benchmark x iterations')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    reader = Reader(open(args.source_text, 'r'))
    reader.parse_text()
    generator = WordGenerator(reader, args.min, args.max, args.allow_doubles)
    user_input = None

    if args.benchmark:
        iterations = args.benchmark
        start_time = datetime.datetime.now()
        for i in range(iterations):
            generator.generate_word()
        elapsed = datetime.datetime.now() - start_time
        print '%s for %s iterations, at %s per iteration' % (
            elapsed, iterations, elapsed.total_seconds() / iterations)
        sys.exit(0)

    if args.generate_songs:
        loads_of_words = [generator.generate_word() for i in range(args.num_words)]
        song_writer = SongWriter(loads_of_words)
    
    while user_input != 'q':
        if args.generate_words:
            word = generator.generate_word()
            print word, count_syllables(word) 
            user_input = raw_input()
        elif args.generate_songs:
            try:
                song = song_writer.get_song(args.rhyming_scheme)
                print '\n'.join(song)
            except IndexError:
                continue
            user_input = raw_input()

import songmaker
import StringIO
import unittest


class TestTrie(unittest.TestCase):

    def test_single_word_can_be_retrieved(self):
        root = songmaker.TrieNode()
        root.add_letters('crunk')
        self.assertTrue('crunk' in root.get_all_words())

    def test_multiple_words_can_be_retrieved(self):
        root = songmaker.TrieNode()
        root.add_letters('smoke')
        root.add_letters('crack')
        all_words = root.get_all_words()
        self.assertTrue('smoke' in all_words)
        self.assertTrue('crack' in all_words)

    def test_multiple_overlapping_words_can_be_retrieved(self):
        root = songmaker.TrieNode()
        overlapping_words = ['necro', 'necrodeath', 'necrogeddon']
        for word in overlapping_words:
            root.add_letters(word)
        all_words = root.get_all_words()
        self.assertItemsEqual(overlapping_words, all_words)

    def test_word_with_prefix(self):
        root = songmaker.TrieNode()
        words = [
            'predeterminism', 'predetermined', 'prevent', 'prevented', 'previous', 'arse']
        for word in words:
            root.add_letters(word)
        self.assertItemsEqual(
            root.words_with_prefix('prev'), ['prevent', 'prevented', 'previous'])
        self.assertItemsEqual(
            root.words_with_prefix('prevent'), ['prevent', 'prevented'])
        self.assertItemsEqual(
            root.words_with_prefix('pred'), ['predeterminism', 'predetermined'])

    def test_get_all_prefixes(self):
        root = songmaker.TrieNode()
        words = ['banana', 'bandana', 'baseball', 'batman', 'smoke', 'crack']
        for word in words:
            root.add_letters(word)
        prefixes = root.get_all_prefixes(num_syllables=1)
        self.assertItemsEqual(prefixes, ['ba', 'cra', 'smo'])

    def test_get_all_prefixes_reversed(self):
        root = songmaker.TrieNode()
        words = ['batman', 'superman', 'fish', 'dish']
        for word in words:
            root.add_letters(word[::-1])
        suffixes = root.get_all_prefixes(num_syllables=1, reverse=True)
        suffixes = [s[::-1] for s in suffixes]
        self.assertItemsEqual(suffixes, ['an', 'ish'])


class TestSyllables(unittest.TestCase):
    ''' Tests for the syllable counting function '''
    def test_various_words(self):
        words = [
            ('motherfucker', 4),
            ('peepee', 2),
            ('flange', 1),
            ('empyrean', 4),
            ('diabolically', 6),
            ('biography', 4),
            ('zwfqrns', 0),
        ]
        for word, syllables in words:
            calculated_syllables = songmaker.count_syllables(word)
            self.assertEqual(calculated_syllables, syllables,
                '%s should have had %s syllables, but had %s' % (
                    word, syllables, calculated_syllables)) 
                

class TestLetter(unittest.TestCase):
    def test_add_follower(self):
        letter = songmaker.Letter('a')
        letter.add_follower('b')
        letter.add_follower('b')
        letter.add_follower('c')
        self.assertEqual(letter.followers['b'], 2)
        self.assertEqual(letter.followers['c'], 1)

    def test_add_position(self):
        letter = songmaker.Letter('a')
        letter.add_position(1)
        letter.add_position(1)
        letter.add_position(2)
        self.assertEqual(letter.positions[1], 2)
        self.assertEqual(letter.positions[2], 1)


class TestReader(unittest.TestCase):

    def test_single_word(self):
        text = StringIO.StringIO('word')
        reader = songmaker.Reader(text)
        reader.parse_text()
        self.assertEqual(reader.letters['w'].followers['o'], 1)
        self.assertEqual(reader.letters['w'].positions[0], 1)

    def test_multiple_words(self):
        text = StringIO.StringIO('two words')
        reader = songmaker.Reader(text)
        reader.parse_text()
        self.assertEqual(reader.letters['w'].followers['o'], 2) 

    def test_mixed_case_and_odd_characters(self):
        text = StringIO.StringIO('wEiRd _sTU.ff\nwhatttt')
        reader = songmaker.Reader(text)
        reader.parse_text()
        self.assertEqual(reader.letters['t'].followers['u'], 1)
        self.assertEqual(reader.letters['u'].followers['f'], 0)

    def test_letters_at_position(self):
        text = StringIO.StringIO('face bard cash mang fish pish czar')
        reader = songmaker.Reader(text)
        reader.parse_text()
        letters = reader.letters_at_position(position=1, num_letters=2)
        self.assertEqual(letters, ['a', 'i'])

    def test_following_letters(self):
        text = StringIO.StringIO('ab ab ab ac ac ad')
        reader = songmaker.Reader(text)
        reader.parse_text()
        letters = reader.following_letters(letter='a', num_letters=2)
        self.assertEqual(letters, ['b', 'c'])

    def test_specific_letters_at_position(self):
        text = StringIO.StringIO('ab ab ab ad ad ac')
        reader = songmaker.Reader(text)
        reader.parse_text()
        letters = reader.specific_letters_at_position(position=1, letters=['c', 'd', 'q'])
        self.assertEqual(letters, ['d', 'c', 'q'])


class TestSongWriter(unittest.TestCase):
    
    def test_construct_maps(self):
        words = ['fantastish', 'fish', 'dish', 'glombar', 'car', 'phone', 'tone']
        song_writer = songmaker.SongWriter(words)
        song_writer.construct_maps()
        self.assertItemsEqual(
            ['fish', 'dish', 'car', 'phone', 'tone'], song_writer.words_by_syllable[1])
        self.assertItemsEqual(['glombar'], song_writer.words_by_syllable[2])
        self.assertItemsEqual(['fantastish'], song_writer.words_by_syllable[3])
        #print song_writer.rhyme_groups
        #ish_group = [g for g in song_writer.rhyme_groups if 'fantastish' in g][0]
        #self.assertItemsEqual(['fantastish', 'fish', 'dish'], ish_group)

    def test_get_parsed_rhyming_scheme(self):
        song_writer = songmaker.SongWriter([])
        raw_scheme = '8a,12b,1c,100a'
        parsed_scheme = song_writer.get_parsed_rhyming_scheme(raw_scheme)
        self.assertEqual(parsed_scheme, [(8, 'a'), (12, 'b'), (1, 'c'), (100, 'a')])


if __name__ == '__main__':
    unittest.main()

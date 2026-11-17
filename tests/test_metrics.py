"""BLEU, ANLS and METEOR (tamtrain/metrics.py). Expected values were checked against NLTK 3.9.1.

    python3 -m unittest discover tests
"""

import unittest

from tamtrain import metrics as M


class Bleu(unittest.TestCase):
    def test_identical_line_scores_one(self):
        words = "இது ஒரு சோதனை வரி ஆகும்".split()
        self.assertAlmostEqual(M.sentence_bleu(words, words), 1.0)

    def test_line_shorter_than_four_words_scores_zero(self):
        # no 4-grams to match: NLTK without smoothing gives (practically) zero
        self.assertEqual(M.sentence_bleu("அ ஆ இ".split(), "அ ஆ இ".split()), 0.0)

    def test_one_wrong_word(self):
        ref = "a b c d e f".split()
        hyp = "a b c d e x".split()
        # precisions 5/6, 4/5, 3/4, 2/3, geometric mean (1/3)^(1/4); no brevity penalty (NLTK: 0.75984)
        self.assertAlmostEqual(M.sentence_bleu(ref, hyp), 0.75984, places=4)

    def test_brevity_penalty(self):
        ref = "a b c d e f g h".split()
        hyp = "a b c d e f".split()
        self.assertAlmostEqual(M.sentence_bleu(ref, hyp), 0.71653, places=4)

    def test_corpus_pools_counts(self):
        refs = ["a b c d".split(), "e f g h".split()]
        self.assertAlmostEqual(M.corpus_bleu(refs, refs), 1.0)
        self.assertEqual(M.corpus_bleu(refs, [[], []]), 0.0)


class Anls(unittest.TestCase):
    def test_values(self):
        self.assertEqual(M.anls("abcd", "abcd"), 1.0)
        self.assertEqual(M.anls("abcd", "abce"), 0.75)
        self.assertEqual(M.anls("abcd", "wxyz"), 0.0)        # distance >= half: scores 0
        self.assertEqual(M.anls("", ""), 1.0)
        self.assertEqual(M.anls("ABC", "abc"), 1.0)          # case-insensitive

    def test_threshold_is_exclusive(self):
        self.assertEqual(M.anls("ab", "ax"), 0.0)            # NL = 0.5 is not below 0.5


class Meteor(unittest.TestCase):
    def test_identical(self):
        words = "a b c d".split()
        # one chunk of 4 matches: penalty 0.5 * (1/4)^3
        self.assertAlmostEqual(M.meteor(words, words), 1 - 0.5 / 64)

    def test_reordered_words_are_penalised(self):
        ref = "a b c d".split()
        self.assertLess(M.meteor(ref, "d c b a".split()), M.meteor(ref, ref))

    def test_no_match_or_empty(self):
        self.assertEqual(M.meteor("a b".split(), "x y".split()), 0.0)
        self.assertEqual(M.meteor("a b".split(), []), 0.0)

    def test_split_word(self):
        # 1 match: P 1/3, R 1/2, F-mean 0.4762, one chunk of one word halves it (NLTK 3.9.1: 0.2381)
        ref, hyp = ["தரையோடு", "வந்தான்"], ["தரை", "யோடு", "வந்தான்"]
        self.assertAlmostEqual(M.meteor(ref, hyp), 0.23810, places=4)


class Similarity(unittest.TestCase):
    def test_keys_and_range(self):
        s = M.similarity(["அ ஆ இ ஈ உ"], ["அ ஆ இ ஈ ஊ"])
        self.assertEqual(set(s), {"bleu", "bleu_corpus", "anls", "meteor"})
        self.assertTrue(all(0 <= v <= 1 for v in s.values()))


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for index_vocab.py (pytest style)
"""
import pytest
import tensorflow as tf
import numpy as np
from src.word2gm_fast.dataprep.index_vocab import make_vocab, build_vocab_table



@pytest.fixture
def vocab_dataset():
    lines = [
        b"the quick brown fox jumps",
        b"the quick brown UNK jumps",
        b"UNK quick brown fox jumps",
        b"the quick brown fox jumps",
        b"lazy dog UNK jumps over",
        b"over the lazy dog jumps",
        b"brown fox jumps over the",
        b"quick brown fox jumps over",
        b"fox jumps over the lazy",
        b"jumps over the lazy dog",
        b"UNK dog jumps over the",
        b"the dog jumps over UNK",
        b"dog jumps over the quick",
        b"jumps over the quick brown",
        b"over the quick brown fox",
    ]
    dataset = tf.data.Dataset.from_tensor_slices(lines)
    return lines, dataset


def test_make_vocab_table(vocab_dataset):
    _, dataset = vocab_dataset
    vocab_table, vocab_list, frequencies = make_vocab(dataset)
    expected_tokens = ["UNK", "the", "quick", "brown", "fox", "jumps", "lazy", "dog", "over"]
    for token in expected_tokens:
        idx = vocab_table.lookup(tf.constant(token)).numpy()
        assert isinstance(idx, (int, np.integer))
    assert vocab_table.lookup(tf.constant("UNK")).numpy() == 0



def test_vocab_table_contents(vocab_dataset):
    lines, _ = vocab_dataset
    vocab_set = set()
    for line in lines:
        tokens = line.decode("utf-8").strip().split()
        vocab_set.update(tokens)
    vocab = ["UNK"] + sorted(tok for tok in vocab_set if tok != "UNK")
    table = build_vocab_table(vocab)
    for i, token in enumerate(vocab):
        assert table.lookup(tf.constant(token)).numpy() == i
    assert table.lookup(tf.constant("notinthevocab")).numpy() == 0


def test_word_index_roundtrip(vocab_dataset):
    """
    Test that for every word in the vocab, word -> index -> word is consistent.
    """
    lines, _ = vocab_dataset
    vocab_set = set()
    for line in lines:
        tokens = line.decode("utf-8").strip().split()
        vocab_set.update(tokens)
    vocab = ["UNK"] + sorted(tok for tok in vocab_set if tok != "UNK")
    table = build_vocab_table(vocab)
    # Simulate vocab.txt as would be written
    idx_to_word = vocab
    for word in vocab:
        idx = table.lookup(tf.constant(word)).numpy()
        # Check that index is in range
        assert 0 <= idx < len(idx_to_word)
        # Check round-trip: word -> idx -> word
        recovered_word = idx_to_word[idx]
        assert recovered_word == word, f"Round-trip failed: {word} -> {idx} -> {recovered_word}"

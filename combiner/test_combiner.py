import combiner
import tempfile
import os
import json
import pprint
from deepdiff import DeepDiff


def assert_dict_equality(d1, d2):
    diff = DeepDiff(d1, d2)
    assert diff == {}


def test_read_write_read(tmpdir):
    d = combiner.file2dict('fixtures/param_card_test.dat')
    written_file = os.path.join(str(tmpdir), 'test.dat')
    combiner.dict2file(d, written_file, overwrite=True)
    test2 = combiner.file2dict(written_file)
    assert_dict_equality(d, test2)

    original = sorted(combiner.read_lines('fixtures/param_card_test.dat'))
    new_file = sorted(combiner.read_lines(written_file))
    assert len(new_file) == len(new_file)
    for line in range(len(original)):
        assert original[line].rstrip() == new_file[line].rstrip()


def test_merge_additional():
    addition = combiner.file2dict('fixtures/addition.dat')
    d = combiner.file2dict('fixtures/param_card_test.dat')
    merged = combiner.mergedicts(d, addition)
    assert_dict_equality(merged, combiner.file2dict('fixtures/param_card_test2.dat'))
    return

if __name__ == '__main__':
    test_read_write('testi')

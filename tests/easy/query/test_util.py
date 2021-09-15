from phc.easy.query.util import flat_map_pipe


def test_flat_map_pipe_with_list():
    def plus_one(x):
        return x + 1

    def duplicate_and_plus_one(x):
        return [x + 1, x + 1]

    def duplicate_and_plus_two(x):
        return [x + 2, x + 2]

    value = flat_map_pipe(
        [1, 2, 3], plus_one, duplicate_and_plus_one, duplicate_and_plus_two
    )

    assert value == [5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7]


def test_flat_map_pipe():
    def plus_one(x):
        return x + 1

    def duplicate_and_plus_one(x):
        return [x + 1, x + 1]

    value = flat_map_pipe(1, plus_one, duplicate_and_plus_one)

    assert value == [3, 3]

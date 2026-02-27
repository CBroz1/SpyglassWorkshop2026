import pytest

from spyglass_workshop import fibonacci
from spyglass_workshop.fibonacci import f, f_list, user_input


@pytest.mark.parametrize(
    "input_n,output_n",
    [
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 3),
        (5, 5),
        (6, 8),
        (7, 13),
        (8, 21),
        (9, 34),
        (10, 55),
        (11, 89),
        (12, 144),
        (13, 233),
        (14, 377),
        (15, 610),
    ],
)
def test_fibonacci(input_n: int, output_n: int) -> None:
    assert fibonacci.f(input_n) == output_n


def test_f_list_empty():
    assert f_list(0) == []


def test_f_list_values():
    assert f_list(5) == [1, 1, 2, 3, 5]
    assert f_list(1) == [1]
    assert f_list(8) == [1, 1, 2, 3, 5, 8, 13, 21]


def test_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "7")
    result = user_input()
    assert "7" in result
    assert str(f(7)) in result


def test_user_input_invalid(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "abc")
    with pytest.raises(ValueError):
        user_input()

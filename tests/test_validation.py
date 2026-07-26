import pytest

from apps.logic.validation import ValidationError, validate_answer


def test_valid_answer_does_not_raise():
    validate_answer(0, 24, "D", "I")


@pytest.mark.parametrize("index", [-1, 24, 50])
def test_out_of_range_index_rejected(index):
    with pytest.raises(ValidationError):
        validate_answer(index, 24, "D", "I")


def test_invalid_style_letter_rejected():
    with pytest.raises(ValidationError):
        validate_answer(0, 24, "X", "I")


def test_same_style_for_most_and_least_rejected():
    with pytest.raises(ValidationError):
        validate_answer(0, 24, "D", "D")

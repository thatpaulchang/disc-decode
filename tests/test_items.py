from apps.logic.items import TETRADS, validate_content


def test_content_is_valid():
    assert len(TETRADS) == 24
    validate_content()

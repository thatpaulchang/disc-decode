VALID_STYLES = {"D", "I", "S", "C"}


class ValidationError(Exception):
    pass


def validate_answer(
    tetrad_index: int, total_tetrads: int, most_style: str, least_style: str
) -> None:
    if not (0 <= tetrad_index < total_tetrads):
        raise ValidationError(f"tetrad_index must be between 0 and {total_tetrads - 1}")
    if most_style not in VALID_STYLES:
        raise ValidationError(f"most_style must be one of {sorted(VALID_STYLES)}")
    if least_style not in VALID_STYLES:
        raise ValidationError(f"least_style must be one of {sorted(VALID_STYLES)}")
    if most_style == least_style:
        raise ValidationError("most_style and least_style must be different")

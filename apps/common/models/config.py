# Top Level Config
COMMON_CHAR_FIELD_MAX_LENGTH = 512

COMMON_NULLABLE_FIELD_CONFIG = {  # user for API based stuff
    "default": None,
    "null": True,
}

COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {  # user for Form/app based stuff
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True,
}
COMMON_DECIMAL_FIELD_CONFIG = {
    "max_digits": 10,
    "decimal_places": 2,
}
COMMON_DECIMAL_FIELD_WITH_DEFAULT_CONFIG = {
    **COMMON_DECIMAL_FIELD_CONFIG,
    "default": 0,
}

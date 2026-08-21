import enum


class ValueEnum(enum.Enum):
    @staticmethod
    def values(enum_class: type[enum.Enum]) -> list[str]:
        return [member.value for member in enum_class]

from abc import ABC


def check_type(func):
    def check(self, other):
        if not isinstance(other, type(self)):
            raise TypeError("unable to compare types")

        return func(self, other)
    return check


class Comparable(ABC):
    ID = 0

    def __init__(self):
        self.id = self.ID
        self.ID += 1

    @check_type
    def __eq__(self, other):
        return other.id == self.id

    @check_type
    def __ne__(self, other):
        return other.id != self.id

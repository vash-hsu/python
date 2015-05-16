#!/usr/bin/env python


def div_mod(dividend, divisor):
    return dividend//divisor, dividend % divisor


class Range:
    def __init__(self, start, end=None, step=1):
        if end is not None:
            self.start = start
            self.end = end
        else:
            self.start = 0
            self.end = start
        self.step = step

    def __len__(self):
        if self.start >= self.end:
            return 0
        (quotient, remainder) = div_mod(self.end - self.start, self.step)
        if 0 == remainder:
            return quotient
        else:
            return quotient + 1

    def __getitem__(self, key):
        if isinstance(key, slice):
            my_range = range(key.start, key.stop, key.step or 1)
            result = []
            for val in my_range:
                if val < self.__len__():
                    result.append(self.step * val + self.start)
            return result
        value = self.step * key + self.start
        if value < self.end:
            return value
        else:
            raise IndexError("key outside of the given range")



#!/usr/bin/env python


def div_mod(dividend, divisor):
    return dividend//divisor, dividend%divisor


class Range:
    def __init__(self, start, end=None, step=1):
        if end is not None:
            self.start = start
            self.end   = end
        else:
            self.start = 0
            self.end   = start
        self.step = step

    def __len__(self):
        (quotient, remainder) = div_mod(self.end - 1 - self.start, self.step)
        if 0 == remainder:
            return quotient + 1
        else:
            return quotient

    def __getitem__(self, key):
        if isinstance(key, slice):
            my_range = range(key.start, key.stop, key.step or 1)
            # return [self.step * val + self.start for val in my_range]
            result = []
            for val in my_range:
                if val <= self.__len__():
                    result.append(self.step * val + self.start)
            return result
        value = self.step * key + self.start
        if value < self.end:
            return value
        else:
            raise IndexError("key outside of the given range")


# to test Range by trigger neo_main_test_for_range with below command line
# python -c "import Range2; Range2.neo_main_test_for_range();"
# however, you still need to use your Eye to find out possible error
# not automatic at all
def neo_main_test_for_range():
    example = Range(3, 17, step=4)
    print 'offset\t\t=', list(range(4))
    print 'example\t\t=', list(example)
    print '-'*40
    for i in xrange(5):
        print 'example[%d:%d]\t= %s' %\
              (i, i+2, str(example[i:i+2]))

if __name__ == '__main__':
    print 'This is main'
    print 'Now, we are going to test Range by neo_main_test_for_range()'
    print '=' * 40
    neo_main_test_for_range()

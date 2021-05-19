"""
JCS compatible JSON serializer for Python 3.x

Copyright 2006-2019 WebPKI.org (http://webpki.org).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from json.encoder import JSONEncoder, _make_iterencode, encode_basestring


def es6_format(value):
    '''Convert a Python double/float into an ES6/V8 compatible string.
    '''
    # convert double/float to str using the native Python formatter
    fvalue = float(value)

    # "0" and "-0" are special cases
    if fvalue == 0:
        return '0'

    # the rest of the algorithm works on the textual representation only
    double = str(fvalue)

    # catch the "inf" and "nan" values returned by str(fvalue)
    if 'n' in double:
        raise ValueError(f'Invalid JSON number: {double}')

    # save sign separately, it doesn't have any role in the algorithm
    if double[0] == '-':
        sign = '-'
        double = double[1:]
    else:
        sign = ''

    # now we should only have valid non-zero values
    q = double.find('e')
    if q > 0:
        # grab the exponent and remove it from the number
        exp_str = double[q:]
        if exp_str[2:3] == '0':
            # supress leading zero on exponents
            exp_str = exp_str[:2] + exp_str[3:]
        double = double[0:q]
        exp_val = int(exp_str[1:])
    else:
        exp_str = ''
        exp_val = 0

    # split number in first + dot + last
    try:
        first, last = double.split('.')
        dot = '.'
    except ValueError:
        first = double
        last = ''
        dot = ''
    else:
        if last == '0':
            # remove trailing .0
            dot = ''
            last = ''

    # split the string into: first + dot + last + exp_str
    if 0 < exp_val < 21:
        # show integers in decimal form up to 21 digits
        first += last
        first += '0' * (exp_val - len(first))
        last = ''
        dot = ''
        exp_str = ''
    elif -7 < exp_val < 0:
        # show small numbers in decimal form with e-6 as lower limit
        last = f'{"0" * (-exp_val + 1)}{first}{last}'
        first = '0'
        dot = '.'
        exp_str = ''

    # concatenate the resulting sub-strings
    return f'{sign}{first}{dot}{last}{exp_str}'


def default(self, o):
    raise TypeError(f'Object of type {o.__class__.__name__} '
                    'is not JSON serializable')


_iterencode = _make_iterencode(
    dict(), default, encode_basestring, None, es6_format,
    ':', ',', True, False, False, _intstr=es6_format)


class Encoder(JSONEncoder):
    skipkeys = False
    ensure_ascii = False
    check_circular = True
    allow_nan = True
    indent = None
    item_separator = ','
    key_separator = ':'

    def __init__(self):
        pass

    @classmethod
    def encode(cls, o):
        '''Return a JSON string representation of a Python data
        structure.
        '''
        if isinstance(o, str):
            return encode_basestring(o)

        # don't pass the iterator directly to ''.join() to get more
        # deatiled exceptions. The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = _iterencode(o, 0)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return ''.join(chunks)


_encode = Encoder.encode


def canonicalize(obj, utf8=True):
    return _encode(obj).encode() if utf8 else _encode(obj)

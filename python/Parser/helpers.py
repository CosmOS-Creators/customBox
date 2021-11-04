from typing import List, Union
import math

# helper decorator to ensure proper naming of functions
def overrides(interface_class):
    def overrider(method):
        assert method.__name__ in dir(interface_class)
        return method

    return overrider


def toInt(hexValue: str):
    if hexValue is None:
        return None
    elif isinstance(hexValue, int):
        return hexValue
    else:
        return int(hexValue, 16)


def toHex(intValue: int, prefix=True):
    hexValue = hex(intValue).upper()
    if not prefix:
        return hexValue.replace("0X", "")
    else:
        return hexValue.replace("X", "x")


def check_alignment(N, align_to):
    if N == align_to:
        return True
    if N == 0:
        return True
    try:
        return N == align_to ** int(round(math.log(N, align_to)))
    except Exception:
        return False


def forceStrList(input: Union[List[str], str]):
    out = input
    valid = True
    if type(input) is str:
        out = [input]
    else:
        if type(input) is list:
            for item in input:
                if not type(item) is str:
                    valid = False
                    break
        else:
            valid = False
        if valid == False:
            raise TypeError(
                f'Allowed types are only str or List[str] but found type "{str(type(input))}" instead.'
            )
    return out


def forceList(input):
    output = input
    if not isinstance(input, list):
        output = [input]
    return output

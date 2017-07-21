import pandas as pd

# Called Vespid code because there is a wasp buzzing around my office right this moment and it's bugging the
# heck out of me. True story.

vespid32_alphabet = "AabCDdEeFGHhKLMNnPRTWXY234567890"

dt = {'Code': str, 'Input': str, 'RD-': str, 'RD+': str, 'cRD-':int, 'cRD+': int}


code34 = pd.read_csv('code34.csv', dtype=dt)
code56 = pd.read_csv('code56.csv', dtype=dt)
code34.set_index('Input', drop=False, inplace=True)
code56.set_index('Input', drop=False, inplace=True)

def bint(i):
    return int(i, 2)

def lpzero(i, width=8):
    """Left pad wih zeros"""
    return '{num:0{width}b}'.format(num=i, width=width)

def count(bitstring):
    """Count 1's"""
    x = int(bitstring, 2)
    acc = 0
    while x > 0:
        acc += (x & 1)
        x >>= 1
    return acc

def get_rd(bitstring):
    """Get the running disparity"""
    c = count(bitstring)
    return c + c - len(bitstring)


def signmap(rd):
    if rd < 0:
        return '-'
    else:
        return '+'


def encode_bs(bitstring, rd=-1):
    x = bitstring[:5]
    y = bitstring[5:]
    x_select = code56.loc[x]
    y_select = code34.loc[y]

    rd = signmap(rd)

    x2 = x_select['RD' + rd]
    rdx = x_select['cRD' + rd]

    rd = signmap(rdx)

    # Anti-5-streak
    #     if x2[-2:] == '11' and y == '111':
    #         print('bork')
    #         y2 = {'-': '0111', '+': '1000'}[rd]

    y2 = y_select['RD' + rd]
    rdy = y_select['cRD' + rd]
    return x2 + y2, rdx + rdy


def decode_bs(bitstring, rd=-1):
    x = bitstring[:6]
    y = bitstring[6:]
    rd = signmap(rd)
    x_select = code56[code56['RD' + rd] == x].ix[0]
    x_decoded = x_select['Input']
    rdx = get_rd(x)

    rd = signmap(rdx)
    y_select = code34[code34['RD' + rd] == y].ix[0]
    y_decoded = y_select['Input']
    rdy = get_rd(y)

    return x_decoded + y_decoded, rdx + rdy

def encode_int(i, rd=-1):
    bs = '{:08b}'.format(i)
    return encode_bs(bs, rd)

def b10_to_vespid(b10):
    a, b = b10[:5], b10[5:]
    a = int(a, 2)
    b = int(b, 2)
    return vespid32_alphabet[a] + vespid32_alphabet[b]

def vespid_pair_to_b10(vp):
    a, b = vp[0], vp[1]
    a = vespid32_alphabet.index(a)
    b = vespid32_alphabet.index(b)
    return lpzero(a, 5) + lpzero(b, 5)

if __name__ == '__main__':
    stream = [1, 2, 42, 13, 250, 111, 255, 0, 5]
    print('Input:', stream)
    msg = []
    rd = -1
    for i in stream:
        packet, rd = encode_int(i, rd)
        msg.append(packet)

    msg_vespid = ''.join([b10_to_vespid(packet) for packet in msg])
    print('Encoded: ', msg)
    print('RD:', [get_rd(packet) for packet in msg])
    print('Vespid: ', msg_vespid)

    dec = []
    rd = -1
    for packet in msg:
        x, rd = decode_bs(packet, rd)
        dec.append(bint(x))

    print('Output:', dec)
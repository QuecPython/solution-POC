import  encoder
from machine import Pin, ExtInt


def encoder_callback(args):
    print(args)


def a(args):
    print("a Encoder callback function executed with args:", args)

def b(args):
    print("b Encoder callback function executed with args:", args)


a_key = ExtInt(ExtInt.GPIO12, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, a)

b_key = ExtInt(ExtInt.GPIO11, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, b)


if __name__ == "__main__":
    a = encoder(Pin.GPIO12, Pin.GPIO11)
    a.set_callback(encoder_callback)
    # pass
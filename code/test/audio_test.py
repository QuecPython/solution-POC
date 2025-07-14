import audio
from machine import Pin



aud = audio.Audio(0)
tts = audio.TTS(0)

p1 = Pin(Pin.GPIO1, Pin.OUT, Pin.PULL_DISABLE, 0)
aud.set_pa(Pin.GPIO1, 4)
aud.set_pa(1)  # Enable PA


aud.aud_tone_play(16, 1000)

# tts.play(1, 1, 2, "Hello")
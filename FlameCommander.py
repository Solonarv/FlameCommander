# get rift wizard module
import inspect 
stack = inspect.stack()

frm = stack[-1]
RiftWizard = inspect.getmodule(frm[0])
# got rift wizard module

import threading
import queue
import pygame
from mods.FlameCommander.monkeypatch import monkeypatch

COMMAND_QUEUE = queue.Queue(maxsize=2)

def gather_input():
    while True:
        line = input()
        COMMAND_QUEUE.put(line)

def tick_command_queue():
    try:
        line = COMMAND_QUEUE.get_nowait()
        exec(line, {'FlameCommander': globals(), **RiftWizard.__dict__})
    except queue.Empty:
        pass
    except Exception as e:
        print(e)



class _HookedClock():
    def __init__(self, *args, **kwargs):
        self._clock = pygame.time.Clock(*args, **kwargs)
    
    def tick(self, *args, **kwargs):
        tick_command_queue()
        self._clock.tick(*args, **kwargs)

@monkeypatch(RiftWizard.PyGameView)
class _PyGameView_Patch():
    @monkeypatch.cfg(inject_old='_old__init__')
    def __init__(self, *args, _old__init__, **kwargs):
        _old__init__(self, *args, **kwargs)
        self.clock = _HookedClock()

input_getter = threading.Thread(target=gather_input, daemon=True)
if not input_getter.is_alive():
    input_getter.start()
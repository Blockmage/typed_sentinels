from typed_sentinels import Sentinel

SENTINEL = Sentinel()
if isinstance(SENTINEL, Sentinel):
    print('Smoke test passed')
else:
    raise TypeError

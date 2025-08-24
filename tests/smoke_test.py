from typed_sentinels import Sentinel

SENTINEL = Sentinel()  # pyright: ignore[reportUnknownVariableType]
if isinstance(SENTINEL, Sentinel):  # pyright: ignore[reportUnnecessaryIsInstance]
    print('Smoke test passed')
else:
    raise TypeError

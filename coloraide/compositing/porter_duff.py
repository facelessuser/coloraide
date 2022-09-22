"""Porter Duff compositing."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod


class PorterDuff(metaclass=ABCMeta):
    """Porter Duff compositing."""

    def __init__(self, cba: float, csa: float) -> None:
        """Initialize."""

        self.cba = cba
        self.csa = csa

    @abstractmethod
    def fa(self) -> float:  # pragma: no cover
        """Calculate `Fa`."""

        raise NotImplementedError('fa is not implemented')

    @abstractmethod
    def fb(self) -> float:  # pragma: no cover
        """Calculate `Fb`."""

        raise NotImplementedError('fb is not implemented')

    def co(self, cb: float, cs: float) -> float:
        """Calculate premultiplied coordinate."""

        return self.csa * self.fa() * cs + self.cba * self.fb() * cb

    def ao(self) -> float:
        """Calculate output alpha."""

        return self.csa * self.fa() + self.cba * self.fb()


class Clear(PorterDuff):
    """Clear."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 0

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 0


class Copy(PorterDuff):
    """Copy."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 0


class Destination(PorterDuff):
    """Destination."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 0

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1


class SourceOver(PorterDuff):
    """Source over."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1 - self.csa


class DestinationOver(PorterDuff):
    """Destination over."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1 - self.cba

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1


class SourceIn(PorterDuff):
    """Source in."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return self.cba

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 0


class DestinationeIn(PorterDuff):
    """Destination in."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 0

    def fb(self) -> float:
        """Calculate `Fb`."""

        return self.csa


class SourceOut(PorterDuff):
    """Source out."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1 - self.cba

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 0


class DestinationOut(PorterDuff):
    """Destination out."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 0

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1 - self.csa


class SourceAtop(PorterDuff):
    """Source atop."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return self.cba

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1 - self.csa


class DestinationAtop(PorterDuff):
    """Destination atop."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1 - self.cba

    def fb(self) -> float:
        """Calculate `Fb`."""

        return self.csa


class XOR(PorterDuff):
    """XOR."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1 - self.cba

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1 - self.csa


class Lighter(PorterDuff):
    """Lighter."""

    def fa(self) -> float:
        """Calculate `Fa`."""

        return 1

    def fb(self) -> float:
        """Calculate `Fb`."""

        return 1


SUPPORTED = {
    'clear': Clear,
    'copy': Copy,
    'destination': Destination,
    'source-over': SourceOver,
    'destination-over': DestinationOver,
    'source-in': SourceIn,
    'destination-in': DestinationeIn,
    'source-out': SourceOut,
    'destination-out': DestinationOut,
    'source-atop': SourceAtop,
    'destination-atop': DestinationAtop,
    'xor': XOR,
    'lighter': Lighter
}


def compositor(name: str) -> type[PorterDuff]:
    """Get the requested compositor."""

    composite = SUPPORTED.get(name)
    if not composite:
        raise ValueError("'{}' compositing is not supported".format(name))
    return composite

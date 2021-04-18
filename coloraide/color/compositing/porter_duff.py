"""Porter Duff compositing."""
from abc import ABCMeta, abstractmethod


class PorterDuff(metaclass=ABCMeta):
    """Porter Duff compositing."""

    def __init__(self, cba, csa):
        """Initialize."""

        self.cba = cba
        self.csa = csa

    @abstractmethod
    def _fa(self):  # pragma: no cover
        """Calculate `Fa`."""

        raise NotImplementedError('fa is not implemented')

    @abstractmethod
    def _fb(self):  # pragma: no cover
        """Calculate `Fb`."""

        raise NotImplementedError('fb is not implemented')

    def co(self, cb, cs):
        """Calculate premultiplied coordinate."""

        return self.csa * self._fa() * cs + self.cba * self._fb() * cb

    def ao(self):
        """Calculate output alpha."""

        return self.csa * self._fa() + self.cba * self._fb()


class Clear(PorterDuff):
    """Clear."""

    def _fa(self):
        """Calculate `Fa`."""

        return 0

    def _fb(self):
        """Calculate `Fb`."""

        return 0


class Copy(PorterDuff):
    """Copy."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1

    def _fb(self):
        """Calculate `Fb`."""

        return 0


class Destination(PorterDuff):
    """Destination."""

    def _fa(self):
        """Calculate `Fa`."""

        return 0

    def _fb(self):
        """Calculate `Fb`."""

        return 1


class SourceOver(PorterDuff):
    """Source over."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1

    def _fb(self):
        """Calculate `Fb`."""

        return 1 - self.csa


class DestinationOver(PorterDuff):
    """Destination over."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1 - self.cba

    def _fb(self):
        """Calculate `Fb`."""

        return 1


class SourceIn(PorterDuff):
    """Source in."""

    def _fa(self):
        """Calculate `Fa`."""

        return self.cba

    def _fb(self):
        """Calculate `Fb`."""

        return 0


class DestinationeIn(PorterDuff):
    """Destination in."""

    def _fa(self):
        """Calculate `Fa`."""

        return 0

    def _fb(self):
        """Calculate `Fb`."""

        return self.csa


class SourceOut(PorterDuff):
    """Source out."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1 - self.cba

    def _fb(self):
        """Calculate `Fb`."""

        return 0


class DestinationOut(PorterDuff):
    """Destination out."""

    def _fa(self):
        """Calculate `Fa`."""

        return 0

    def _fb(self):
        """Calculate `Fb`."""

        return 1 - self.csa


class SourceAtop(PorterDuff):
    """Source atop."""

    def _fa(self):
        """Calculate `Fa`."""

        return self.cba

    def _fb(self):
        """Calculate `Fb`."""

        return 1 - self.csa


class DestinationAtop(PorterDuff):
    """Destination atop."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1 - self.cba

    def _fb(self):
        """Calculate `Fb`."""

        return self.csa


class XOR(PorterDuff):
    """XOR."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1 - self.cba

    def _fb(self):
        """Calculate `Fb`."""

        return 1 - self.csa


class Lighter(PorterDuff):
    """Lighter."""

    def _fa(self):
        """Calculate `Fa`."""

        return 1

    def _fb(self):
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


def compositor(name):
    """Get the requested compositor."""

    name = name.lower()
    if name not in SUPPORTED:
        raise ValueError("'{}' compositing is not supported".format(name))
    return SUPPORTED[name]

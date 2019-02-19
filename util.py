import numpy as np


class Point(np.ndarray):
    """
    Abstraction of a n-dimensional point based on a numpy array.
    """

    def __new__(cls, input_array, dtype=float):
        obj = np.array(input_array, dtype=dtype).view(cls)
        return obj

    def with_(self, i, val):
        els = np.array(self)
        els[i] = val
        return Point(els, dtype=self.dtype)

    @staticmethod
    def as_int(input_array):
        return Point(input_array, dtype=int)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]


class Bounds:
    """
    A class for keeping track of bounds. Works with Point instances,
    and automatically updates n-dimensional lo/hi values.
    """

    INITIAL_POINT = Point(None)

    def __init__(self, initial_pts=None, dtype=float):
        initial_pts = [] if initial_pts is None else initial_pts
        self.dtype = dtype
        self.lo = Bounds.INITIAL_POINT
        self.hi = Bounds.INITIAL_POINT
        for pt in initial_pts: self.update(pt)

    def update(self, pt):
        if self.lo is Bounds.INITIAL_POINT:
            self.lo = Point(pt, self.dtype)
            self.hi = Point(pt, self.dtype)
            return self

        iter_ = enumerate(zip(self.lo, self.hi, pt))
        for i, (val_lo, val_hi, val_pt) in iter_:
            if val_pt < val_lo:
                self.lo[i] = val_pt
            elif val_pt > val_hi:
                self.hi[i] = val_pt

        return self

    @property
    def range_(self):
        return self.hi - self.lo

    def __repr__(self):
        return "Bounds(lo={}, hi={})".format(self.lo, self.hi)

"""
scalar field abstractions for the staggered grid
"""
import inspect
import numpy as np
from PyMPDATA.impl.enumerations import INVALID_INIT_VALUE, INVALID_NULL_VALUE
from PyMPDATA.impl.meta import META_HALO_VALID, META_IS_NULL
from PyMPDATA.boundary_conditions import Constant
from PyMPDATA.impl.field import Field


class ScalarField(Field):
    """ n-dimensional scalar field including halo data """
    def __init__(self, data: np.ndarray, halo: int, boundary_conditions: tuple):
        super().__init__(
            grid=data.shape,
            boundary_conditions=boundary_conditions,
            halo=halo,
            dtype=data.dtype
        )

        for dim_length in data.shape:
            assert halo <= dim_length
        for boundary_condition in boundary_conditions:
            assert not inspect.isclass(boundary_condition)

        shape_with_halo = tuple(data.shape[i] + 2 * halo for i in range(self.n_dims))
        self.data = np.full(shape_with_halo, INVALID_INIT_VALUE, dtype=data.dtype)
        self.impl_data = (self.data,)
        self.domain = tuple(
            slice(halo, self.data.shape[i] - halo)
            for i in range(self.n_dims)
        )
        self.get()[:] = data[:]

    @staticmethod
    def clone(field, dtype=None):
        dtype = dtype or field.dtype
        # note: copy=False is OK as the ctor anyhow copies the data to an array with halo
        return ScalarField(
            field.get().astype(dtype, copy=False),
            field.halo,
            field.boundary_conditions
        )

    def get(self) -> np.ndarray:  # note: actually a view is returned
        results = self.data[self.domain]
        return results

    @staticmethod
    def make_null(n_dims, traversals):
        null = ScalarField(
            np.empty([INVALID_NULL_VALUE]*n_dims),
            halo=0,
            boundary_conditions=[Constant(np.nan)] * n_dims
        )
        null.meta[META_HALO_VALID] = True
        null.meta[META_IS_NULL] = True
        null.assemble(traversals)
        return null

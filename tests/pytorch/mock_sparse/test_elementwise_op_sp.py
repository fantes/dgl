import numpy as np
import pytest
import dgl
import dgl.backend as F
import torch
import numpy
import operator
from dgl.mock_sparse import SparseMatrix
parametrize_idtype = pytest.mark.parametrize("idtype", [F.int32, F.int64])
parametrize_dtype = pytest.mark.parametrize('dtype', [F.float32, F.float64])

def all_close_sparse(A, B):
    assert torch.allclose(A.indices(), B.indices())
    assert torch.allclose(A.values(), B.values())
    assert A.shape == B.shape

@parametrize_idtype
@parametrize_dtype
@pytest.mark.parametrize('op', [operator.add, operator.sub, operator.mul, operator.truediv])
def test_sparse_op_sparse(idtype, dtype, op):
    rowA = torch.tensor([1, 0, 2, 7, 1])
    colA = torch.tensor([0, 49, 2, 1, 7])
    valA = torch.rand(len(rowA))
    A = SparseMatrix(rowA, colA, valA, shape=(10, 50))
    w = torch.rand(len(rowA))
    A1 = SparseMatrix(rowA, colA, w, shape=(10, 50))

    rowB = torch.tensor([1, 9, 2, 7, 1, 1, 0])
    colB = torch.tensor([0, 1, 2, 1, 7, 11, 15])
    valB = torch.rand(len(rowB))
    B = SparseMatrix(rowB, colB, valB, shape=(10, 50))

    def _test():
        if op is not operator.truediv:
            all_close_sparse(op(A.adj, A1.adj), op(A, A1).adj)
            all_close_sparse(op(A.adj, B.adj), op(A, B).adj)
        else:
            # sparse div is not supported in PyTorch
            assert np.allclose(op(A, A1).val, op(A.val, A1.val), rtol=1e-4, atol=1e-4)
    _test()

@parametrize_idtype
@parametrize_dtype
@pytest.mark.parametrize('v_scalar', [2, 2.5])
def test_sparse_op_scalar(idtype, dtype, v_scalar):
    row = torch.randint(1, 500, (100,))
    col = torch.randint(1, 500, (100,))
    val = torch.rand(100)
    A = SparseMatrix(row, col, val)
    all_close_sparse(A.adj * v_scalar, (A * v_scalar).adj)
    all_close_sparse(A.adj / v_scalar, (A / v_scalar).adj)
    all_close_sparse(pow(A.adj, v_scalar), pow(A, v_scalar).adj)

@parametrize_idtype
@parametrize_dtype
@pytest.mark.parametrize('v_scalar', [2, 2.5])
def test_scalar_op_sparse(idtype, dtype, v_scalar):
    row = torch.randint(1, 500, (100,))
    col = torch.randint(1, 500, (100,))
    val = torch.rand(100)
    A = SparseMatrix(row, col, val)
    all_close_sparse(v_scalar * A.adj, (v_scalar * A).adj)

def test_expose_op():
    rowA = torch.tensor([1, 0, 2, 7, 1])
    colA = torch.tensor([0, 49, 2, 1, 7])
    A = dgl.mock_sparse.SparseMatrix(rowA, colA, shape=(10, 50))
    dgl.mock_sparse.add(A, A)
    dgl.mock_sparse.sub(A, A)
    dgl.mock_sparse.mul(A, A)
    dgl.mock_sparse.div(A, A)

if __name__ == '__main__':
    test_sparse_op_sparse()
    test_sparse_op_scalar()
    test_scalar_op_sparse()
    test_expose_op()

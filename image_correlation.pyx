import Cython
import numpy as np
cimport numpy as np
from libc.math cimport sqrt

def corr(float[:,:] array1, float[:,:] array2, int[:] im_array):
    # define integer variables
    cdef int i, j, r, r1, idx
    # define float variables
    cdef float dx, dy, dist, min_dist

    r = array1.shape[0]
    r1 = array2.shape[0]

    # define output arrays
    cdef int [:] min_idx = np.zeros([r1], dtype=np.int32)
    cdef int [:] val = np.zeros([r1], dtype=np.int32)

    for i in range(r1):
        min_dist = 1000 # set to artificially large value
        for j in range(r):
            dx = array1[j, 0] - array2[i, 0]
            dy = array1[j, 1] - array2[i, 1]

            dist = sqrt(dx*dx + dy*dy)

            # check if current distance is less than min distance
            if dist < min_dist:
                min_dist = dist
                min_idx[i] = j

        # index into image and get value
        val[i] = im_array[min_idx[i]]

    return np.asarray(val)

# this function finds the minimum cost path through the graph
# inputs are the global and local costs
# optional arguments for the start and end indices
import numpy as np


def optimum(C, L, start_idx=[], end_idx=[]):
    # check if list is empty, if so identify start and end pair automatically
    if not start_idx:
        # get end cost first
        end_idx1, end_cost1 = end(C, L)

        # invert C and L in order to determine the start pair
        start_idx1, start_cost1 = start(C, L, end_idx1)

        # now get start cost first
        start_idx2, start_cost2 = start(C, L)
        end_idx2, end_cost2 = end(C, L, start_idx2)

        # get optimum cost starting depending on which has the lower cost
        if start_cost1 < start_cost2:
            start_idx = start_idx1
        else:
            start_idx = start_idx2

        if end_cost1 < end_cost2:
            end_idx = end_idx1
        else:
            end_idx = end_idx2

    # remove indices of the cost matrix that are outside of the start and end points
    C = C[start_idx[0]:end_idx[0], :, start_idx[1]:end_idx[1]]
    # using the end index determine the angle to start from (min cumlulative cost)
    angle_idx = np.argmin(C[-1, :, -1])
    # get the optimum path from end index to start index
    optimum_path, _, _ = path(C, C.shape[0]-1, C.shape[2]-1, angle_idx)

    # add the removed start indices back so we get the correct original image numbers
    optimum_path = np.asarray(optimum_path)
    optimum_path[:, 0] = optimum_path[:, 0] + start_idx[0]
    optimum_path[:, 1] = optimum_path[:, 1] + start_idx[1]
    return optimum_path


def path(C, BL_idx, FU_idx, angle_idx):
    # this function determine the costs through each path
    # set how many bl and fu images to find min over
    step = 1

    # create list for path cost
    path_cost = [C[BL_idx, angle_idx, FU_idx]]
    path_idx = [(BL_idx, FU_idx, angle_idx)]
    temp=np.empty(C.shape)
    temp[:] = np.inf
    # iterate until reach the end
    while FU_idx > 0 and BL_idx > 0:
        angle_idx = np.arange(angle_idx - step, angle_idx + step + 1)

        angle_idx[angle_idx < 0] = angle_idx[angle_idx < 0] + C.shape[1]
        angle_idx[angle_idx >= C.shape[1]] = angle_idx[angle_idx >= C.shape[1]] - C.shape[1]
        temp1=temp.copy()
        temp1[BL_idx-step:BL_idx+step, angle_idx, FU_idx-step:FU_idx+step] = C[BL_idx-step:BL_idx+step, angle_idx, FU_idx-step:FU_idx+step]
        temp1[BL_idx, angle_idx, FU_idx] = np.inf
        # get index of the min value
        idx = np.argmin(temp1)
        #C[BL_idx-step, angle_idx, FU_idx] # BL=i-1, FU=k
        #C[BL_idx-step, angle_idx, FU_idx-step] # BL=i-1, FU=k-1
        #C[BL_idx, angle_idx, FU_idx-step] # BL=i, FU=k-1

        BL_idx, angle_idx, FU_idx = np.unravel_index(idx, C.shape)
        # check if we are indexing over a smaller array and impact of this on the index

        # append the cost
        path_cost.append(C[BL_idx, angle_idx, FU_idx])
        # append list of tuples with BL_idx, FU_idx and angle
        path_idx.append((BL_idx, FU_idx, angle_idx))

    return path_idx, sum(path_cost)/float(len(path_cost)), len(path_cost)


def end(C, L, idx=0):
    # find ending frame pair (i - baseline, k - follow-up)

    # only include the frames within the range specified by the ending pair
    if idx != 0:
        C = C[idx[0]:, :, idx[1]:]
        L = L[idx[0]:, :, idx[1]:]

    # assume min overlap of 20 frames (10 mm)
    min_overlap = 10

    # hold the BL frame fixed i.e. we are identifying the FU frame with min cost
    BL_idx1 = C.shape[0] - 1 # subtract 1 as index begins at 0
    FU_idx1 = np.linspace(min_overlap, C.shape[2]-1, (C.shape[2]-1)/min_overlap, dtype=np.int)

    # initialize array for cost1 (mean cost of path) of shape (j, k)
    cost1 = np.zeros([C.shape[1], FU_idx1.shape[0]])
    n_e1 = np.zeros([C.shape[1], FU_idx1.shape[0]])
    path_cost1 = np.zeros([C.shape[1], FU_idx1.shape[0]])

    for k in range(0, FU_idx1.shape[0]):
        for start_angle in range(0, C.shape[1]):
            _, cost1[start_angle, k], n_e1[start_angle, k] = path(C, BL_idx1, FU_idx1[-k-1], start_angle)
            # ALTERNATIVE INTERPRETATION (cost is originating cost divided by path length)
            path_cost1[start_angle, k] = C[BL_idx1, start_angle, FU_idx1[-k-1]]/n_e1[start_angle, k]

    # repeat holding FU frame fixed
    FU_idx2 = C.shape[2] - 1
    BL_idx2 = np.linspace(min_overlap, C.shape[0] - 1, (C.shape[0]-1)/min_overlap, dtype=np.int)

    # initialize array for cost2 shape (i, j)
    #cost2 = np.zeros([C.shape[1],  BL_idx2.shape[0]])
    #n_e2 = np.zeros([C.shape[1], BL_idx2.shape[0]])
    cost2 = np.zeros([BL_idx2.shape[0], C.shape[1]])
    n_e2 = np.zeros([BL_idx2.shape[0], C.shape[1]])
    path_cost2 = np.zeros([BL_idx2.shape[0], C.shape[1]])

    for i in range(0, BL_idx2.shape[0]):
        for start_angle in range(0, C.shape[1]):
            _, cost2[i, start_angle], n_e2[i, start_angle] = path(C, BL_idx2[-i-1], FU_idx2, start_angle)
            path_cost2[i, start_angle] = C[BL_idx2[-i-1], start_angle, FU_idx2] / n_e2[i, start_angle]

    # invert path costs as they have been indexed start to end but have been determined start to end
    # i.e. path_cost1 - last column is now the cost from last FU frame to first BL frame
    # i.e. path_cost2 - last row is now the cost from last BL frame to first FU frame
    path_cost1 = path_cost1[:, ::-1]
    path_cost2 = path_cost2[::-1, :]

    # identify cumulative costs for pre-specified
    # G1 is global cost in going from end pair to 0,0
    G1 = path_cost1 + L[:,:, FU_idx1] # BL held fixed
    # G2 is global cost in going from end pair to 0,0
    G2 = np.expand_dims(path_cost2, axis = 2) + L[BL_idx2, :, :] # FU held fixed
    G1 = path_cost1 + L[-1, :, FU_idx1].T
    G2 = path_cost2 + L[BL_idx2, :, -1]
    # Two methods, not sure which one is correct
    # Method1
    # find ending frames (I, K) with min cost
    #E = np.argmin(G1)
    #E_FU = np.unravel_index(E, G1.shape)[2]

    #E = np.argmin(G2)
    #E_BL = np.unravel_index(E, G2.shape)[0]

    #E = [BL_idx2[-E_BL], FU_idx1[-E_FU]]
    #E_cost = G1

    # Method2
    #E = np.argmin(G1[-1, :, :])
    #E_FU = np.unravel_index(E, G1[-1, :, :].shape)[1]
    #E = np.argmin(G2[:, :, -1])
    #E_BL = np.unravel_index(E, G2[-1,:,:].shape)[0]

    #E = [BL_idx2[-E_BL], FU_idx1[-E_FU]]

    # Method3
    if np.min(G1) < np.min(G2):
        E = np.argmin(G1)

        # BL and FU index
        E_FU = np.unravel_index(E, G1.shape)[1]
        E = [BL_idx1, FU_idx1[E_FU]]
        E_cost = np.min(G1)
    elif np.min(G2) < np.min(G1):
        E = np.argmin(G2) #np.unravel_index(np.argmin(G2), (G2.shape))

        # BL and FU index
        E_BL = np.unravel_index(E, G2.shape)[0]
        E = [BL_idx2[E_BL], FU_idx2]
        E_cost = np.min(G2)
    elif np.min(G1) == np.min(G2):
        # the last frame has been selected in both cases
        E = [BL_idx1, FU_idx2]
        E_cost = np.min(G2)

    return E, E_cost

def start(C, L, idx=0):
    # find starting frame pair (i - baseline, k - follow-up)

    # only include the frames within the range specified by the ending pair
    if idx != 0:
        C = C[:idx[0], :, :idx[1]]
        L = L[:idx[0], :, :idx[1]]

    # transpose 3D array
    Ctran = C[::-1, :, ::-1]
    Ltran = L[::-1, :, ::-1]


    # constrain the search range over the minimum required BL/FU overlap
    # set constraint to 50 images
    #Cconstrain = Ctran[-50:, :, -50:]
    #Lconstrain = Ltran[-50:, :, -50:]
    # determine index and cost of starting frames
    #E, E_cost = end(Cconstrain, Lconstrain)
    E, E_cost = end(Ctran, Ltran)


    # need to subtract from end in order to get start indices
    E[0] = C.shape[0] - E[0]
    E[1] = C.shape[2] - E[1]
    return E, E_cost
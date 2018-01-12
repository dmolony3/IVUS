import numpy as np


def compute(CorrPv, CorrPa, CorrPt, CorrArea, w=0.1, angle=0):
    # determine number of BL and FU images as well as number of angular steps
    num_BL = CorrPv.shape[0]
    num_FU = CorrPv.shape[2]
    steps = CorrPv.shape[1]

    # initialize weights
    alpha = 0.4
    beta = 0.4
    gamma = 0.2
    if angle == 0:
        angle = 360/steps

    # max angle to determine cost over
    theta_twist = 2*angle


    # initialize instantaneous cost and accumulated cost
    #cost = np.zeros([num_BL, steps, num_FU])
    cost = alpha*(1 - CorrPv) + beta*(1 - CorrPa) + gamma*(1 - CorrPt) + CorrArea
    COST = np.zeros([num_BL, steps, num_FU])

    # initialize first and bottom row
    COST[0, :, 0] = cost[0, :, 0]

    # initialize cost across the floor of the cost matrix (FU image =1)
    for i in range(1, num_BL):
        for j in range(0, steps):
            #for j in range(0, 360, angle):
            # define range of angles to calculate cost over
            current_angle = j*angle
            delta_theta = np.arange(current_angle - theta_twist, current_angle + theta_twist+1)
            delta_theta[delta_theta < 0] = delta_theta[delta_theta < 0] + 360
            delta_theta[delta_theta >= 360] = delta_theta[delta_theta >= 360] - 360
            # divide by the angle in order to get the correct index over the input spacing
            delta_theta = np.unique(delta_theta / angle)
            # Global cost delta_theta[delta_theta % angle == 0]
            COST[i, j, 0] = min(COST[i - 1, delta_theta, 0] + cost[i, j, 0])

    # initialize cost across the left side of the cost matrix (BL image =1)
    for k in range(1, num_FU):
        for j in range(0, steps):

            # define range of angles to calculate cost over
            current_angle = j*angle
            delta_theta = np.arange(current_angle - theta_twist, current_angle + theta_twist)
            delta_theta[delta_theta < 0] = delta_theta[delta_theta < 0] + 360
            delta_theta[delta_theta >= 360] = delta_theta[delta_theta >= 360] - 360
            # divide by the angle in order to get the correct index over the input spacing
            delta_theta = np.unique(delta_theta / angle)
            # Global cost
            COST[0, j, k] = min(COST[0, delta_theta, k - 1] + cost[0, j, k])

    # determine cost for remaining images
    for i in range(1, num_BL):
        for k in range(1, num_FU):
            for j in range(0, steps):    # define range of angles to calculate cost over
                current_angle = j * angle
                delta_theta = np.arange(current_angle - theta_twist, current_angle + theta_twist)
                delta_theta[delta_theta < 0] = delta_theta[delta_theta < 0] + 360
                delta_theta[delta_theta >= 360] = delta_theta[delta_theta >= 360] - 360
                # divide by the angle in order to get the correct index over the input spacing
                delta_theta = np.unique(delta_theta / angle)

                  # include penalization for different relative twisting between BL and FU
                twist_pen = w*(delta_theta/theta_twist)*cost[i ,j, k]
                # determine global cost
                COST[i, j, k] = cost[i, j, k] + min(min(COST[i-1, delta_theta, k] + twist_pen),
                                                    min(COST[i, delta_theta, k-1] + twist_pen),
                                                    min(COST[i-1,delta_theta, k-1] + twist_pen))

    return COST, cost

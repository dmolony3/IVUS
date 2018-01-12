import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def eval(auto_coreg, manual_coreg):

    error_frame = np.zeros([auto_coreg.shape[0], 1])
    error_angle = np.zeros([auto_coreg.shape[0], 1])
    i=0
    for frame in auto_coreg[:, 0]:
        # find manual and FU frame corresponding to BL frame, average in case of more than one frame
        manual_FU = np.round(np.mean(manual_coreg[manual_coreg[:, 0] == frame, 1]))
        auto_FU = np.round(np.mean(auto_coreg[auto_coreg[:, 0] == frame, 1]))
        error_frame[i] = abs(auto_FU - manual_FU)

        if manual_coreg.shape[1] > 2:
            manual_angle = np.round(np.mean(manual_coreg[manual_coreg[:, 0] == frame, 2]))
            auto_angle = np.round(np.mean(auto_coreg[auto_coreg[:, 0] == frame, 2]))
            error_angle[i] = min(abs(auto_angle - manual_angle), 360 - abs(auto_angle - manual_angle))
        i += 1

    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot(auto_coreg[:, 0], auto_coreg[:, 2], auto_coreg[:, 1], 'r')
    if manual_coreg.shape[1] > 2:
        ax.plot(manual_coreg[:, 0], manual_coreg[:, 2], manual_coreg[:, 1], 'g.')
    else:
        ax.plot(manual_coreg[:, 0], np.zeros([manual_coreg.shape[0], 1]), manual_coreg[:, 1], 'g.')
    ax.set_xlabel('BL frame no.')
    ax.set_ylabel('registration angle')
    ax.set_zlabel('FU frame no.')
    plt.show()

    return error_frame, error_angle
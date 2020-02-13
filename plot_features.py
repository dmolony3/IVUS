from matplotlib import pyplot as plt


def plot(CostPv, CostPa, CostPt, Costarea, BL, FU):

    total_cost = CostPv[BL, :, FU] + CostPa[BL, :, FU] + CostPt[BL, :, FU] + Costarea[BL, :, FU]
    total_cost = total_cost/total_cost.max()
    plt.figure()
    plt.plot(CostPv[BL, :, FU], 'r', label='Perivacular')
    plt.plot(CostPa[BL, :, FU], 'g', label='Plaque')
    plt.plot(CostPt[BL, :, FU], 'c', label='Thickness')
    plt.plot(Costarea[BL, :, FU], 'k', label='Area')
    plt.plot(total_cost, 'k', label='Total')
    plt.legend(loc='upper right')
    plt.xlabel('Circumferential angle (degrees')
    plt.ylabel('Cost')
    plt.show()

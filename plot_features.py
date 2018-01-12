from matplotlib import pyplot as plt


def plot(CostPv, CostPa, CostPt, Costarea, BL, FU):

    total_cost = CostPv[BL, :, FU] + CostPa[BL, :, FU] + CostPt[BL, :, FU] + Costarea[BL, :, FU]
    total_cost = total_cost/total_cost.max()
    plt.figure()
    plt.plot(CostPv[BL, :, FU], 'r')
    plt.plot(CostPa[BL, :, FU], 'g')
    plt.plot(CostPt[BL, :, FU], 'c')
    plt.plot(Costarea[BL, :, FU], 'k')
    plt.plot(total_cost[BL, :, FU], 'k')

    plt.show()

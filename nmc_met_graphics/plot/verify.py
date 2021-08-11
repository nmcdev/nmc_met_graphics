# _*_ coding: utf-8 _*_

# Copyright (c) 2021 NMC Developers.
# Distributed under the terms of the GPL V3 License.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def quality_visual(ax=None):
    """Visualizing Multiple Measures of Forecast Quality
    refer to:
      Roebber, P.J., 2009: Visualizing Multiple Measures of Forecast Quality.
      Wea. Forecasting, 24, 601-608, https://doi.org/10.1175/2008WAF2222159.1

    Keyword Arguments:
        ax {matplotlib.axes} -- matplotlib axes instance (default: {None})
    """

    # set up figure
    if ax is None:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

    # modifying rc settings
    plt.rc('font', size=20)
    plt.rc('axes', linewidth=3)
    plt.rc('xtick.major', size=14, width=3)
    plt.rc('ytick.major', size=14, width=3)
    plt.rc('xtick.minor', size=8, width=1)
    plt.rc('ytick.minor', size=8, width=1)

    # define SR
    SR = np.arange(0.0, 1.01, 0.01)

    # draw BS lines
    BSs = [0.3, 0.5, 0.8, 1.0, 1.3, 1.5, 2.0, 3.0, 5.0, 10.0]
    for bs in BSs:
        ax.plot(SR, bs*SR, color="black",
                linewidth=1, linestyle='--', label="BIAS")
        if bs < 1.0:
            ax.text(1.02, bs, str(bs), fontsize=16)
        elif bs > 1.0:
            ax.text(1.0-(bs-1)/bs, 1.02, str(bs), ha='center', fontsize=16)
        else:
            ax.text(1.02, 1.02, '1.0', fontsize=16)

    # draw CSI line
    CSIs = np.arange(0.1, 1.0, 0.1)
    x_pos = [0.5, 0.576, 0.652, 0.728, 0.804, 0.88, 0.88, 0.93, 0.97]
    for i, csi in enumerate(CSIs):
        pod = SR/(SR/csi + SR - 1.0)
        pod[pod < 0] = np.nan
        ax.plot(SR, pod, color="black", linewidth=1, label="CSI")
        ax.text(x_pos[i], x_pos[i]/(x_pos[i]/csi + x_pos[i] - 1.0),
                "{:.1f}".format(csi), backgroundcolor="white", fontsize=12)

    # set axis style
    majorLocator = MultipleLocator(0.1)
    minorLocator = MultipleLocator(0.02)
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_minor_locator(minorLocator)
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.01)
    ax.set_xlabel('Success Ratio (1-FAR)')
    ax.set_ylabel('Probability of Detection (POD)')

    # restore default rc settings
    plt.rcdefaults()
    return ax

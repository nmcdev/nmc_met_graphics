# _*_ coding: utf-8 _*_

# Copyright (c) 2022 NMC Developers.
# Distributed under the terms of the GPL V3 License.

import warnings
import numpy as np
import xarray as xr
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


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/toolbox/binary_events_skill_score.py

class Contingency:
    """Compute skill scores for binary events.

    TODO:
    - What to do when array has nans or are masked arrays?
    """

    def __init__(self, observed, forecasted):
        """
        Create a contingency table for two binary fields.

        Number of hits (a), false alarms (b), misses (c), and correct
        rejections (d).

        Parameters
        ----------
        forecasted : array_like, bool
            Array of True/False if the event was forecasted
        observed :array_like, bool
            Array of True/False if the event was observed
        """
        self.observed = observed
        self.forecasted = forecasted

        self._validate()

        self.a = self.hits
        self.b = self.false_alarms
        self.c = self.misses
        self.d = self.correct_rejections

        self.n_forecasted = self.a + self.b
        self.n_observed = self.a + self.c
        self.n = self.a + self.b + self.c + self.d

        # Other useful values
        self.a_random = (self.a + self.b) * (self.a + self.c) / self.n
        self.d_random = (self.b + self.d) * (self.c + self.d) / self.n

    def _validate(self):
        assert np.shape(self.observed) == np.shape(
            self.forecasted
        ), "input must be the same shape"
        self.observed = self.observed.astype(bool)
        self.forecasted = self.forecasted.astype(bool)

    def __str__(self):
        """print the contingency table"""
        if isinstance(self.hits, xr.DataArray):
            msg = [
                "          {:^20}".format("Observed"),
                "         │{:^10}{:^10}│ {:>10}".format("Yes", "No", "Total"),
                "─────────┼────────────────────┼─────────────",
                " Fxx Yes │{:^10,}{:^10,}│ {:>10,}".format(
                    self.a.item(), self.b.item(), self.a.item() + self.b.item()
                ),
                " Fxx No  │{:^10,}{:^10,}│ {:>10,}".format(
                    self.c.item(), self.d.item(), self.c.item() + self.d.item()
                ),
                "─────────┼────────────────────┼─────────────",
                "Total    │{:^10,}{:^10,}│ {:>10,}".format(
                    self.a.item() + self.c.item(),
                    self.b.item() + self.d.item(),
                    self.n.item(),
                ),
            ]
        else:
            msg = [
                "          {:^20}".format("Observed"),
                "         │{:^10}{:^10}│ {:>10}".format("Yes", "No", "Total"),
                "─────────┼────────────────────┼─────────────",
                " Fxx Yes │{:^10,}{:^10,}│ {:>10,}".format(
                    self.a, self.b, self.a + self.b
                ),
                " Fxx No  │{:^10,}{:^10,}│ {:>10,}".format(
                    self.c, self.d, self.c + self.d
                ),
                "─────────┼────────────────────┼─────────────",
                "Total    │{:^10,}{:^10,}│ {:>10,}".format(
                    self.a + self.c, self.b + self.d, self.n
                ),
            ]
        return "\n".join(msg)

    @property
    def hits(self):
        """Condition is forecasted and observed (a)"""
        return np.nansum(np.logical_and(self.forecasted, self.observed))

    @property
    def false_alarms(self):
        """Condition is forecasted but not observed (b)"""
        return np.nansum(self.forecasted) - self.a

    @property
    def misses(self):
        """Condition is observed but not forecasted (c)"""
        return np.nansum(self.observed) - self.a

    @property
    def correct_rejections(self):
        """Condition is not forecasted and not observed (d)"""
        return np.nansum(np.logical_and(~self.forecasted, ~self.observed))

    def base_rate(self):
        """The probability that an event will be observed."""
        s = (self.a + self.c) / (self.n)
        return s

    def forecast_rate(self):
        """The probability that an event will forecasted."""
        r = (self.a + self.b) / (self.n)
        return r

    def frequency_bias(self):
        """
        Total events forecasted divided by the total events observed. Bias Score.
        "How did the forecast frequency of 'yes' events compare to the observed
        frequency of 'yes' events?"
        - Perfect Score: B = 1
        - Underforecast: B < 1
        - Overforcast  : B > 1

        Does not measure how well the forecast corresponds to the observations,
        only measures relative frequencies.
        If condition is never observed (0), then B is infinity.
        """
        B = (self.a + self.b) / (self.a + self.c)
        return B

    def hit_rate(self):
        """
        Also known as Probability of Detection (POD) or recall.
        "What fraction of the observed 'yes' events were correctly forecast?"
        - Range [0,1];
        - Perfect Score = 1

        Sensitive to hits, but ignores false alarms. Very sensitive to the
        climatological frequency of the event. Good for rare events. Can be
        artificially improved by issuing more 'yes' forecasts to increase the
        number of hits. Should be used in conjunction with the false alarm ratio.
        """
        H = self.a / (self.a + self.c)
        return H

    def probability_of_detection(self):
        """Same as hit_rate."""
        return self.hit_rate()

    def false_alarm_rate(self):
        """
        Also known as Probability of False Detection (POFD)
        "What fraction of the observed 'no' events were incorrectly forecast as
        'yes'?"
        - Perfect Score = 0

        Sensitive to false alarms, but ignores misses. Can be artificially improved
        by issuing fewer 'yes' forecasts to reduce the number of false alarms.
        Not often reported for deterministic forecasts, but is an important
        component of the Relative Operating Characteristic (ROC) used widely for
        probabilistic forecasts.

        .. warning:: Do not confuse with false_alarm_ratio (FAR)
        """
        F = self.b / (self.b + self.d)
        return F

    def probability_of_false_detection(self):
        """Same as false_alarm_rate."""
        return self.false_alarm_rate()

    def false_alarm_ratio(self):
        """
        Often abbreviated as FAR. "What fraction of the predicted 'yes'
        events actually did not occur (i.e., were false alarms)?"
        - Perfect Score = 0

        Sensitive to false alarms, but ignores misses. Very sensitive to the
        climatological frequency of the event. Should be used in conjunction with
        the hit rate.

        .. warning:: Do not confuse with false_alarm_rate
        """
        FAR = self.b / (self.a + self.b)
        return FAR

    def success_ratio(self):
        """
        The same as 1-FAR (false alarm ratio) or precision.
        "What fraction of the forecast 'yes' events were correctly
        observed?"
        - Perfect Score = 1

        Gives information about the likelihood of an observed event, given that it
        was forecast. It is sensitive to false alarms but ignores misses.
        """
        SR = self.a / (self.a + self.b)
        return SR

    def f1_score(self):
        """
        F1 Score is the harmonic mean of the precision and recall (success ratio and hit rate)
        It is a measure of performance for the positive cases.
        https://en.wikipedia.org/wiki/F-score
        - Perfect Score = 1 (perfect success ratio and hit rate)
        - Lowest value = 0
        """
        precision = self.success_ratio()
        recall = self.hit_rate()
        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score

    def proportion_correct(self):
        """
        Also known as Accuracy.
        "Overall, what fraction of the forecasts were correct?"
        - Perfect Score = 1
        - Worst case = 0

        """
        PC = (self.a + self.d) / (self.n)
        return PC

    def critical_success_index(self):
        """
        Also known as Threat Score (TS) or Gilbert Score (GS).
        "How well did the forecast 'yes' events correspond to the observed 'yes'
        events?"
        - Perfect Score = 1

        The total number of correct event forecasts (hits) divided by the total
        number of event forecasts plus the number of misses. Strongly dependent
        on the base rate because it is not affected by the number of non-event
        forecasts that are not observed (correct rejections).

        Measures the fraction of observed and/or forecast events that were
        correctly predicted. It can be thought of as the accuracy when correct
        negatives have been removed from consideration, that is, TS is only
        concerned with forecasts that count. Sensitive to hits, penalizes both
        misses and false alarms. Does not distinguish source of forecast error.
        Depends on climatological frequency of events (poorer scores for rarer
        events) since some hits can occur purely due to random chance.
        """
        CSI = self.a / (self.a + self.b + self.c)
        return CSI

    def gilbert_skill_score(self):
        """
        Also known as the Equitable Threat Score (ETS).
        Widely used for the verification of deterministic forecasts of rare events
        such as precipitation above a large threshold. However, the score is not
        "equitable."
        "How well did the forecast 'yes' events correspond to the observed 'yes'
        events (accounting for hits due to chance)?"
        - Range: [-1/3, 1]
        - Zero is no skill
        - Perfect Score = 1

        Measures the fraction of observed and/or forecast events that were
        correctly predicted, adjusted for hits associated with random chance
        (for example, it is easier to correctly forecast rain occurrence in a wet
        climate than in a dry climate). The ETS is often used in the verification
        of rainfall in NWP models because its "equitability" allows scores to be
        compared more fairly across different regimes. Sensitive to hits. Because
        it penalizes both misses and false alarms in the same way, it does not
        distinguish the source of forecast error.

        `a_random` is the number of hits expected a forecasts independent
        of observations (pure chance). Since (n) is in the denominator, GSS depends
        explicitly on the number of correct rejections (d). In other words, `a_r`
        is the expected (a) for a random forecast with the same forecast rate (r)
        and base rate (s).
        """
        GSS = (self.a - self.a_random) / (self.a + self.b + self.c - self.a_random)
        return GSS

    def equitable_threat_score(self):
        """Same as the gilbert skill score"""
        ETS = self.gilbert_skill_score()
        return ETS

    def heidke_skill_score(self):
        """
        Based on the proportion correct that takes into account the number of hits
        due to chance.
        "What was the accuracy of the forecast relative to that of random chance?"
        - Range [-1,1]
        - Zero is no skill
        - Perfect score = 1

        `a_random` is the number of hits expected a forecasts independent
        of observations (pure chance).
        `d_random` is ...
        """
        HSS = (self.a + self.d - self.a_random - self.d_random) / (
            self.n - self.a_random - self.d_random
        )
        return HSS

    def peirce_skill_score(self):
        """
        Also known as the Hanssen and Kuipers discriminant or True Skill Statistic.
        Ratio of hits to total number of events observed minus the ratio of false
        alarms to total number of non-events observed (i.e. PSS = H-F).
        "How well did the forecast separate the 'yes' events from the 'no' events?"
        - Range [-1,1]
        - Perfect Score = 1

        Uses all elements in contingency table. Does not depend on climatological
        event frequency. The expression is identical to PSS = POD - POFD, but the
        Peirce Skill score can also be interpreted as
        ``(accuracy for events) + (accuracy for non-events) - 1``

        For rare events, PSS is unduly weighted toward the first term (same as
        POD), so this score may be more useful for more frequent events.
        """
        PSS = (self.a * self.d - self.b * self.c) / (
            (self.b + self.d) * (self.a + self.c)
        )
        return PSS

    def clayton_skill_score(self):
        """
        Ratio of hits to total number of events forecast minus the ratio of correct
        rejections to total number of non-events forecast.
        Analogous to the PSS except it is stratified on the forecasts rather than
        the observations.
        """
        CSS = self.a / (self.a + self.b) - self.c / (self.c + self.d)
        return CSS

    def doolittle_skill_score(self):
        """
        Doolittle Skill Score

        Also known as the Matthews correlation coefficient??

        The doolittle skill score may be wrong.
        Consult https://stats.stackexchange.com/a/485796/220885 and
        https://doi.org/10.1080/00031305.2015.1086686
        """
        warnings.warn(
            "The doolittle skill score may be wrong. Consult https://stats.stackexchange.com/a/485796/220885 and https://doi.org/10.1080/00031305.2015.1086686"
        )
        DSS = (self.a * self.d - self.b * self.c) / np.sqrt(
            (self.a + self.b)(self.c + self.d)(self.a + self.c)(self.b + self.d)
        )
        return DSS

    def log_of_odds_ratio(self):
        """Log of Odds Ratio"""
        theta = self.a * self.d / (self.b * self.c)
        LOR = np.log(theta)
        return LOR

    def odds_ratio_skill_score(self):
        """Odds Ratio Skill Score"""
        Q = (self.a * self.d - self.b * self.c) / (self.a * self.d + self.b * self.c)
        return Q

    def fractions_skill_score(
        self, width=None, radius=None, generic_filter_kwargs={}, verbose=True
    ):
        r"""
        Compute the Fractions Skill Score.

        As the size of the neighborhood is increased, the sharpness is
        reduced.

        References
        ----------
        Roberts, N.M. and H.W. Lean, 2008: Scale-Selective Verification
        of Rainfall Accumulations from High-Resolution Forecasts of
        Convective Events. Mon. Wea. Rev., 136, 78–97,
        https://doi.org/10.1175/2007MWR2123.1

        Parameters
        ----------
        width : int
            Width of gridpoints for the square neighborhood footprint.
            Preferably an odd number so that the width is equal in
            all directions. Used if `radius` is None.
        radius : int
            Radius of gridpoints for the circular neighborhood footprint.
            Used only if `width` is None.
        generic_filter_kwargs : dict
            By default, the generic_filter uses ``mode='constant'`` and
            ``cval=0``, which assigns points outside the domain a value
            of zero. The Roberts paper handled the edges in this way.
            You may modify this if you wish.
        """
        import scipy.ndimage as ndimage

        def fraction(values):
            """Compute the fraction of the area that is True."""
            return np.sum(values) / np.size(values)

        def radial_footprint(radius):
            """A footprint with the given radius"""
            y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
            footprint = x ** 2 + y ** 2 <= radius ** 2
            footprint = 1 * footprint.astype(float)
            return footprint

        assert (
            np.sum([width is None, radius is None]) == 1
        ), "`width` or `radius` must be specified, but not both."

        ################################################################
        # Generate fractions for each neighborhood
        # "These quantities assess the spatial density in the binary fields."
        #                                          - Roberts et al. 2008

        generic_filter_kwargs.setdefault("mode", "constant")
        generic_filter_kwargs.setdefault("cval", 0)

        return_this = {}

        if width is not None:
            if verbose:
                print(f"Box footprint width: {width}x{width} grid boxes")
            return_this["method"] = ("Box Footprint", width)
            generic_filter_kwargs["size"] = width
        elif radius is not None:
            if verbose:
                print(f"Circular footprint radius: {radius} grid boxes")
            return_this["method"] = ("Circular Footprint", radius)
            generic_filter_kwargs["footprint"] = radial_footprint(radius)

        # NOTE: If an xarray DataSet is given, a numpy array will be returned.
        if verbose:
            print("Generate the fractions at each grid point.")
        obs_fracs = ndimage.generic_filter(
            self.observed.astype(float), fraction, **generic_filter_kwargs
        )
        fxx_fracs = ndimage.generic_filter(
            self.forecasted.astype(float), fraction, **generic_filter_kwargs
        )

        ################################################################
        # Compute the Fractions Skill Score:
        if verbose:
            print("Compute fractions skill score")
        MSE = np.mean((obs_fracs - fxx_fracs) ** 2)
        MSE_ref = np.mean(obs_fracs ** 2) + np.mean(fxx_fracs ** 2)

        FSS = 1 - (MSE / MSE_ref)

        return_this["FSS"] = (FSS,)
        return_this["Observed_Fraction"] = obs_fracs
        return_this["Forecasted_Fraction"] = fxx_fracs
        return_this["generic_filter_kwargs"] = generic_filter_kwargs

        return return_this


########################################################################
########################################################################
########################################################################
# Performance Diagrams


def f1_diagram(ax=None, **kwargs):
    """
    Related to precision and recall (success ratio and hit rate)
    Very similar to Critical Success Index (CSI)
    """
    if ax is None:
        ax = plt.gca()

    precision = np.arange(0.01, 1.01, 0.01)  # success ratio
    recall = np.arange(0.01, 1.01, 0.01)  # hit rate or probability of detection

    x, y = np.meshgrid(precision, recall)

    F1_score = 2 * (x * y) / (x + y)

    kwargs.setdefault("levels", np.arange(0, 1, 0.1))
    kwargs.setdefault("colors", ".8")
    kwargs.setdefault("zorder", 0)

    c = plt.contour(x, y, F1_score, **kwargs)
    c.clabel(manual=[(0.8, 0.8), (0.8, 0.5), (0.8, 0.3), (0.8, 0.1)], zorder=0)

    ax.set_title("F1 Score")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")

    ax.set_xticks(np.arange(0, 1.1, 0.2))
    ax.set_yticks(np.arange(0, 1.1, 0.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return ax


def csi_diagram(ax=None, **kwargs):
    """
    Critical Success Index is related to POD and 1-FAR (Success Ratio SR).

    From Roebber 2009
    https://doi.org/10.1175/2008WAF2222159.1
    """
    if ax is None:
        ax = plt.gca()

    POD = np.arange(0.01, 1.01, 0.01)  # probability of detetion or hit rate
    SR = np.arange(0.01, 1.01, 0.01)  # 1-false alarm ratio (success ratio)

    x, y = np.meshgrid(POD, SR)

    csi_score = 1 / ((1 / x) + (1 / y) - 1)

    kwargs.setdefault("levels", np.arange(0, 1, 0.1))
    kwargs.setdefault("colors", ".8")
    kwargs.setdefault("zorder", 0)

    c = plt.contour(x, y, csi_score, **kwargs)
    c.clabel(manual=[(0.8, i) for i in np.arange(0.1, 1, 0.2)], zorder=0)

    ax.set_title("Critical Success Index Curve")
    ax.set_xlabel("Success Ratio (1-FAR)")
    ax.set_ylabel("Probability of Detection (POD)")

    ax.set_xticks(np.arange(0, 1.1, 0.2))
    ax.set_yticks(np.arange(0, 1.1, 0.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return ax


def bias_diagram(ax=None, **kwargs):
    """
    Bias is related to POD and 1-FAR (Success Ratio SR).

    From Roebber 2009
    https://doi.org/10.1175/2008WAF2222159.1
    """
    if ax is None:
        ax = plt.gca()

    POD = np.arange(0.01, 1.01, 0.01)  # probability of detetion or hit rate
    SR = np.arange(0.01, 1.01, 0.01)  # 1-false alarm ratio (success ratio)

    x, y = np.meshgrid(POD, SR)

    bias = np.transpose(x / y)

    kwargs.setdefault("levels", [0.3, 0.5, 0.8, 1, 1.3, 1.5, 2, 3, 5, 10])
    kwargs.setdefault("colors", ".8")
    kwargs.setdefault("zorder", 0)
    kwargs.setdefault("linestyles", "--")

    cs = plt.contour(x, y, bias, **kwargs)
    # cs.clabel(
    #    #manual=[(.8, i) for i in np.arange(.1,1,.2)],
    #    zorder=0)
    labelAtEdge(
        kwargs["levels"], cs, ax, r"%.1f", side="top", pad=0.005, color=kwargs["colors"]
    )
    levs = kwargs["levels"][:3]
    labelAtEdge(levs, cs, ax, r"%.1f", side="right", pad=0.005, color=kwargs["colors"])
    # labelAtEdge(kwargs['levels'], cs, ax, r'%.2f $C^{\circ}$', side='right', pad=0.005, color='r', fontsize=12)
    # labelAtEdge(kwargs['levels'], cs, ax, '%.2f', side='left', pad=0.005, color='r', fontsize=10)

    ax.set_title("Bias\n")
    ax.set_xlabel("Success Ratio (1-FAR)")
    ax.set_ylabel("Probability of Detection (POD)")

    ax.set_xticks(np.arange(0, 1.1, 0.2))
    ax.set_yticks(np.arange(0, 1.1, 0.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return ax


def reliability_diagram(ax=None, **kwargs):
    """
    Related to Observed relative frequency and forecast probabilty
    See also: https://met.readthedocs.io/en/latest/Users_Guide/appendixC.html#reliability-diagram
    """
    if ax is None:
        ax = plt.gca()

    kwargs.setdefault("color", ".7")
    kwargs.setdefault("ls", "--")
    kwargs.setdefault("zorder", 0)

    plt.plot([0, 1], [0, 1])
    plt.text(
        0.5,
        0.54,
        "perfect reliability",
        fontsize=20,
        fontweight="bold",
        rotation=45,
        color=kwargs["color"],
        va="center",
        ha="center",
    )

    ax.set_title("Reliability Diagram")
    ax.set_xlabel("Forecast Probability")
    ax.set_ylabel("Observed Relative Frequency")

    ax.set_xticks(np.arange(0, 1.1, 0.2))
    ax.set_yticks(np.arange(0, 1.1, 0.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return ax


def labelAtEdge(levels, cs, ax, fmt, side="both", pad=0.005, **kwargs):
    """Label contour lines at the edge of plot

    Solution from here:
    https://numbersmithy.com/how-to-label-the-contour-lines-at-the-edge-of-a-matplotlib-plot/

    Args:
        levels (1d array): contour levels.
        cs (QuadContourSet obj): the return value of contour() function.
        ax (Axes obj): matplotlib axis.
        fmt (str): formating string to format the label texts. E.g. '%.2f' for
            floating point values with 2 demical places.
    Keyword Args:
        side (str): on which side of the plot intersections of contour lines
            and plot boundary are checked. Could be: 'left', 'right', 'top',
            'bottom' or 'all'. E.g. 'left' means only intersections of contour
            lines and left plot boundary will be labeled. 'all' means all 4
            edges.
        pad (float): padding to add between plot edge and label text.
        **kwargs: additional keyword arguments to control texts. E.g. fontsize,
            color.
    """

    from matplotlib.transforms import Bbox

    collections = cs.collections
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    bbox = Bbox.from_bounds(xlim[0], ylim[0], xlim[1] - xlim[0], ylim[1] - ylim[0])

    eps = 1e-5  # error for checking boundary intersection

    # -----------Loop through contour levels-----------
    for ii, lii in enumerate(levels):

        cii = collections[ii]  # contours for level lii
        pathsii = cii.get_paths()  # the Paths for these contours
        if len(pathsii) == 0:
            continue

        for pjj in pathsii:

            # check first whether the contour intersects the axis boundary
            if not pjj.intersects_bbox(bbox, False):  # False significant here
                continue

            xjj = pjj.vertices[:, 0]
            yjj = pjj.vertices[:, 1]

            # intersection with the left edge
            if side in ["left", "all"]:
                inter_idx = np.where(abs(xjj - xlim[0]) <= eps)[0]
                for kk in inter_idx:
                    inter_x = xjj[kk]
                    inter_y = yjj[kk]

                    ax.text(
                        inter_x - pad,
                        inter_y,
                        fmt % lii,
                        ha="right",
                        va="center",
                        **kwargs,
                    )

            # intersection with the right edge
            if side in ["right", "all"]:
                inter_idx = np.where(abs(xjj - xlim[1]) <= eps)[0]
                for kk in inter_idx:
                    inter_x = xjj[kk]
                    inter_y = yjj[kk]

                    ax.text(
                        inter_x + pad,
                        inter_y,
                        fmt % lii,
                        ha="left",
                        va="center",
                        **kwargs,
                    )

            # intersection with the bottom edge
            if side in ["bottom", "all"]:
                inter_idx = np.where(abs(yjj - ylim[0]) <= eps)[0]
                for kk in inter_idx:
                    inter_x = xjj[kk]
                    inter_y = yjj[kk]

                    ax.text(
                        inter_x - pad,
                        inter_y,
                        fmt % lii,
                        ha="center",
                        va="top",
                        **kwargs,
                    )

            # intersection with the top edge
            if side in ["top", "all"]:
                inter_idx = np.where(abs(yjj - ylim[-1]) <= eps)[0]
                for kk in inter_idx:
                    inter_x = xjj[kk]
                    inter_y = yjj[kk]

                    ax.text(
                        inter_x + pad,
                        inter_y,
                        fmt % lii,
                        ha="center",
                        va="bottom",
                        **kwargs,
                    )
    return

## Brian Blaylock
## May 7, 2021

"""
==========
Statistics
==========
"""
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt


class paired_diff_ttest:
    def __init__(self, a, b, alpha=0.05):
        """
        Paired Difference T-test for means

        Test if the means between two samples are different given that
        the samples are dependant on one another.

        Parameters
        ----------
        a, b : array_like
            Two vectors to compare. Must be of equal length.
        alpha : float
            Significance level. The confidence interval is 1-alpha.
            Alpha represents the probability of rejecting the null
            hypothesis given the null hypothesis is assumed true.
            Default 0.05 is for a 95% confidence interval.

        References
        ----------
        [1] https://www.youtube.com/watch?v=90BHKgVQrEQ
        [2] https://www.reneshbedre.com/blog/ttest.html#paired-t-test-dependent-t-test
        [3] https://www.jmp.com/en_gb/statistics-knowledge-portal/t-test/paired-t-test.html
        [4] https://en.wikipedia.org/wiki/Statistical_significance
        [5] https://blog.minitab.com/en/alphas-p-values-confidence-intervals-oh-my

        Returns
        -------
        mean, marginal_error, and tuple of the confidence lower and upper bound.

        Example
        -------
        >>> a = [45, 23, 87, 42, 50]
        >>> b = [52, 25, 96, 48, 55]
        >>> ttest = paired_diff_ttest(a, b)
        >>> ttest.plot()
        >>> ttest
        """
        self.alpha = alpha  # Significance level
        self.ci = 1 - alpha  # Confidence Interval

        self.diff = np.subtract(b, a)  # converts to numpy array
        self.mean = np.mean(self.diff)
        self.std = np.std(self.diff, ddof=1)
        self.n = len(self.diff)

        # T critical value
        self.t_critical = scipy.stats.t.ppf(q=1 - alpha / 2, df=(self.n - 1))

        # Marginal error
        self.err = self.t_critical * self.std / np.sqrt(self.n)

        # Critical Interval 95% confidence interval
        self.upper_bound = self.mean + self.err
        self.lower_bound = self.mean - self.err
        self.bounds = [self.lower_bound, self.upper_bound]

        # Interpretation
        if self.lower_bound > 0:
            self.interpretation = (
                f"b mean is greater than a mean with {self.ci:.3%} confidence."
            )
        elif self.upper_bound < 0:
            self.interpretation = (
                f"b mean is less than a mean with {self.ci:.3%} confidence."
            )
        else:
            self.interpretation = f"The difference between a and b are not statistically significant with {self.ci:.3%} confidence."

    def __repr__(self):
        msg = [
            "Paired Difference T-test for Means",
            "-----------------------------------",
            f"Number of Samples: {self.n}",
            f"Mean of differences: {self.mean:.3f}",
            f"Standard deviation of differences: {self.std:.3f}",
            f"Significance Level alpha : {self.alpha}",
            f"Confidence Interval : {self.ci:%}",
            f"T critical value: {self.t_critical:.3f}",
            f"Marginal Error: {self.err:.3f}",
            f"Lower Bound: {self.lower_bound:.3f}",
            f"Upper Bound: {self.upper_bound:.3f}",
            f"{self.interpretation}",
        ]
        return "\n".join(msg)

    def plot(self, ax=None):
        """Simple Plot"""
        if ax is None:
            ax = plt.gca()

        ax.errorbar(
            0,
            self.mean,
            yerr=self.err,
            marker="o",
            capsize=3,
            elinewidth=0.5,
            ecolor=".5",
            label="mean and interval",
        )
        ax.scatter(
            np.zeros_like(self.diff),
            self.diff,
            alpha=0.5,
            marker=".",
            color=".5",
            label="pair-wise differences",
        )
        ax.axhline(0, color="k", linestyle="--")

        # Cosmetics
        ax.set_title("Paired Difference T-test for Means")
        ax.set_ylabel("Difference (b-a)")
        ax.legend()

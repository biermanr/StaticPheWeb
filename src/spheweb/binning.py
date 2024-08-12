"""Classes to bin SNPs from TSV/CSV/MLMA files into windows for plotting."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class Binner(ABC):
    """Abstract base class for binning SNPs into windows for plotting."""

    @abstractmethod
    def validate(self, data_file: Path) -> None:
        """Validate the input data file."""
        pass

    @abstractmethod
    def bin(self, data_file: Path) -> Dict[str, Any]:
        """Bin the input data file."""
        pass


class WindowBinner(Binner):
    """Simple window-based binning of SNPs."""

    def __init__(self, window_size: int):
        """Initialize the window binner with a window size."""
        self.window_size = window_size

    def bin(self, data_file: Path) -> Dict[str, Any]:
        """Perform the binning of SNPs into windows."""
        return {"TODO": "implement"}


class PheWebBinner(Binner):
    """PheWeb-style binning of SNPs."""


# TODO IMPLEMENT
#   def __init__(self) -> None:
#       self._peak_best_variant = None
#       self._peak_last_chrpos = None
#       self._peak_pq = MaxPriorityQueue()
#       self._unbinned_variant_pq = MaxPriorityQueue()
#       self._bins = {}  # like {<chrom>: {<pos // bin_length>: [{chrom, startpos, qvals}]}}
#       self._qval_bin_size = (
#           0.05  # this makes 200 bins for the minimum-allowed y-axis covering 0-10
#       )
#       self._num_significant_in_current_peak = 0  # num variants stronger than manhattan_peak_variant_counting_pval_threshold


#    def bin(self, data_file: Path) -> Dict[str, Any]:
#        """Perform PheWeb binning."""
#        if variant["pval"] != 0:
#            qval = -math.log10(variant["pval"])
#            if qval > 40:
#                self._qval_bin_size = 0.2  # this makes 200 bins for a y-axis extending past 40 (but folded so that the lower half is 0-20)
#            elif qval > 20:
#                self._qval_bin_size = (
#                    0.1  # this makes 200-400 bins for a y-axis extending up to 20-40.
#                )
#
#        if variant["pval"] < conf.get_manhattan_peak_pval_threshold():  # part of a peak
#            if self._peak_best_variant is None:  # open a new peak
#                self._peak_best_variant = variant
#                self._peak_last_chrpos = (variant["chrom"], variant["pos"])
#                self._num_significant_in_current_peak = (
#                    1
#                    if variant["pval"]
#                    < conf.get_manhattan_peak_variant_counting_pval_threshold()
#                    else 0
#                )
#            elif (
#                self._peak_last_chrpos[0] == variant["chrom"]
#                and self._peak_last_chrpos[1] + conf.get_manhattan_peak_sprawl_dist()
#                > variant["pos"]
#            ):  # extend current peak
#                if (
#                    variant["pval"]
#                    < conf.get_manhattan_peak_variant_counting_pval_threshold()
#                ):
#                    self._num_significant_in_current_peak += 1
#                self._peak_last_chrpos = (variant["chrom"], variant["pos"])
#                if variant["pval"] >= self._peak_best_variant["pval"]:
#                    self._maybe_bin_variant(variant)
#                else:
#                    self._maybe_bin_variant(self._peak_best_variant)
#                    self._peak_best_variant = variant
#            else:  # close old peak and open new peak
#                self._peak_best_variant["num_significant_in_peak"] = (
#                    self._num_significant_in_current_peak
#                )
#                self._num_significant_in_current_peak = (
#                    1
#                    if variant["pval"]
#                    < conf.get_manhattan_peak_variant_counting_pval_threshold()
#                    else 0
#                )
#                self._maybe_peak_variant(self._peak_best_variant)
#                self._peak_best_variant = variant
#                self._peak_last_chrpos = (variant["chrom"], variant["pos"])
#        else:
#            self._maybe_bin_variant(variant)
#
#        pass

"""Legacy binning code from PheWeb retained for compatibility and tests."""

import heapq
import math
from typing import Any, Iterable, Optional

from . import binning, parsing


class LegacyBinner(binning.Binner):  # type: ignore
    """PheWeb-style binning of SNPs."""

    def __init__(self) -> None:
        """Initialize the binner."""
        self._peak_best_variant: Optional[dict[str, Any]] = None
        self._peak_last_chrpos: tuple[str, int] = ("", 0)
        self._peak_pq: MaxPriorityQueue = MaxPriorityQueue()
        self._unbinned_variant_pq: MaxPriorityQueue = MaxPriorityQueue()
        self._bins: dict[
            int, Any
        ] = {}  # like {<chrom>: {<pos // bin_length>: [{chrom, startpos, qvals}]}}
        self._qval_bin_size = (
            0.05  # this makes 200 bins for the minimum-allowed y-axis covering 0-10
        )
        self._num_significant_in_current_peak = 0  # num variants stronger than manhattan_peak_variant_counting_pval_threshold

        # TODO
        # NOTE: hardcoding PheWeb `conf` values here
        # NOTE: the goal is just to validate SPheWeb binning for now
        self.BIN_LENGTH = int(3e6)
        self.manhattan_peak_pval_threshold = 1e-6
        self.manhattan_peak_variant_counting_pval_threshold = 5e-8
        self.manhattan_peak_sprawl_dist = 200_000
        self.manhattan_peak_max_count = 500
        self.manhattan_num_unbinned = 500

        # chrom_order_list = [str(i) for i in range(1,22+1)] + ['X', 'Y', 'MT'] #RB hardcoding dog chrs
        chrom_order_list = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",
            "34",
            "35",
            "36",
            "37",
            "38",
            "39",
        ]
        self.chrom_order = {
            chrom: index for index, chrom in enumerate(chrom_order_list)
        }

    def bin(self, parser: parsing.Parser) -> dict[str, Any]:
        """Perform PheWeb binning."""
        for v in parser:
            v = dict(v)  # convert pydantic model to dict to add previously used fields
            self.process_variant(v)

        return self.get_result()

    def process_variant(self, variant: dict[str, Any]) -> None:
        """Process a single variant."""
        if variant["pval"] != 0:
            qval = -math.log10(variant["pval"])
            if qval > 40:
                self._qval_bin_size = 0.2  # this makes 200 bins for a y-axis extending past 40 (but folded so that the lower half is 0-20)
            elif qval > 20:
                self._qval_bin_size = (
                    0.1  # this makes 200-400 bins for a y-axis extending up to 20-40.
                )

        if variant["pval"] < self.manhattan_peak_pval_threshold:  # part of a peak
            if self._peak_best_variant is None:  # open a new peak
                self._peak_best_variant = variant
                self._peak_last_chrpos = (variant["chrom"], variant["pos"])
                self._num_significant_in_current_peak = (
                    1
                    if variant["pval"]
                    < self.manhattan_peak_variant_counting_pval_threshold
                    else 0
                )
            elif (
                self._peak_last_chrpos[0] == variant["chrom"]
                and self._peak_last_chrpos[1] + self.manhattan_peak_sprawl_dist
                > variant["pos"]
            ):  # extend current peak
                if (
                    variant["pval"]
                    < self.manhattan_peak_variant_counting_pval_threshold
                ):
                    self._num_significant_in_current_peak += 1
                self._peak_last_chrpos = (variant["chrom"], variant["pos"])
                if variant["pval"] >= self._peak_best_variant["pval"]:
                    self._maybe_bin_variant(variant)
                else:
                    self._maybe_bin_variant(self._peak_best_variant)
                    self._peak_best_variant = variant
            else:  # close old peak and open new peak
                self._peak_best_variant["num_significant_in_peak"] = (
                    self._num_significant_in_current_peak
                )
                self._num_significant_in_current_peak = (
                    1
                    if variant["pval"]
                    < self.manhattan_peak_variant_counting_pval_threshold
                    else 0
                )
                self._maybe_peak_variant(self._peak_best_variant)
                self._peak_best_variant = variant
                self._peak_last_chrpos = (variant["chrom"], variant["pos"])
        else:
            self._maybe_bin_variant(variant)

    def _maybe_peak_variant(self, variant: dict[str, Any]) -> None:
        """Add a variant to the peak queue if it's significant enough."""
        self._peak_pq.add_and_keep_size(
            variant,
            variant["pval"],
            size=self.manhattan_peak_max_count,
            popped_callback=self._maybe_bin_variant,
        )

    def _maybe_bin_variant(self, variant: dict[str, Any]) -> None:
        """Add a variant to the unbinned queue if it's significant enough."""
        self._unbinned_variant_pq.add_and_keep_size(
            variant,
            variant["pval"],
            size=self.manhattan_num_unbinned,
            popped_callback=self._bin_variant,
        )

    def _bin_variant(self, variant: dict[str, Any]) -> None:
        """Add a variant to the appropriate bin."""
        chrom_idx = self.chrom_order[variant["chrom"]]
        if chrom_idx not in self._bins:
            self._bins[chrom_idx] = {}
        pos_bin_id = variant["pos"] // self.BIN_LENGTH
        if pos_bin_id not in self._bins[chrom_idx]:
            self._bins[chrom_idx][pos_bin_id] = {
                "chrom": variant["chrom"],
                "startpos": pos_bin_id * self.BIN_LENGTH,
                "qvals": set(),
            }
        qval = (
            math.inf
            if variant["pval"] == 0
            else self._rounded(-math.log10(variant["pval"]))
        )
        self._bins[chrom_idx][pos_bin_id]["qvals"].add(qval)

    def get_result(self) -> dict[str, Any]:
        """Return the binned variants."""
        # this can only be called once
        if getattr(self, "already_got_result", None):
            raise Exception()
        self.already_got_result = True

        if self._peak_best_variant:
            # self._peak_best_variant['num_significant_in_peak'] = self._num_significant_in_current_peak
            self._maybe_peak_variant(self._peak_best_variant)

        peaks = list(self._peak_pq.pop_all())
        # for peak in peaks: peak['peak'] = True
        unbinned_variants = list(self._unbinned_variant_pq.pop_all())
        unbinned_variants = sorted(
            unbinned_variants + peaks, key=(lambda variant: variant["pval"])
        )

        # unroll dict-of-dict-of-array `bins` into array `variant_bins`
        variant_bins = []
        for chrom_idx in sorted(self._bins.keys()):
            for pos_bin_id in sorted(self._bins[chrom_idx].keys()):
                b = self._bins[chrom_idx][pos_bin_id]
                assert len(b["qvals"]) > 0
                b["qvals"], b["qval_extents"] = self._get_qvals_and_qval_extents(
                    b["qvals"]
                )
                b["pos"] = int(b["startpos"] + self.BIN_LENGTH / 2)
                del b["startpos"]
                variant_bins.append(b)

        return {
            "variant_bins": variant_bins,
            "unbinned_variants": [dict(v) for v in unbinned_variants],
        }

    def _rounded(self, qval: float) -> float:
        """Round a q-value to the nearest bin."""
        # round down to the nearest multiple of `self._qval_bin_size`, then add 1/2 of `self._qval_bin_size` to be in the middle of the bin
        x = qval // self._qval_bin_size * self._qval_bin_size + self._qval_bin_size / 2
        return round(
            x, 3
        )  # trim `0.35000000000000003` to `0.35` for convenience and network request size

    def _get_qvals_and_qval_extents(
        self, qvals: list[float]
    ) -> tuple[list[float], list[tuple[float, float]]]:
        qvals = sorted(self._rounded(qval) for qval in qvals)
        extents = [(qvals[0], qvals[0])]
        for q in qvals:
            if q <= extents[-1][1] + self._qval_bin_size * 1.1:
                extents[-1] = (extents[-1][0], q)
            else:
                extents.append((q, q))
        rv_qvals, rv_qval_extents = [], []
        for start, end in extents:
            if start == end:
                rv_qvals.append(start)
            else:
                rv_qval_extents.append((start, end))
        return (rv_qvals, rv_qval_extents)


class MaxPriorityQueue:
    """`.pop()` returns the item with the largest priority.

    `.popall()` iteratively `.pop()`s until empty.
    priorities must be comparable.
    `item` can be anything.
    """

    class ComparesFalse:
        """A class that compares False to everything."""

        __eq__ = __lt__ = __gt__ = lambda s, o: False

    def __init__(self) -> None:
        """Initialize the queue."""
        self._q: list[
            tuple[float, Any, dict[str, Any]]
        ] = []  # a heap-property-satisfying list like [(priority, ComparesFalse(), item), ...]

    def add(self, item: dict[str, Any], priority: float) -> None:
        """Add an item to the queue."""
        heapq.heappush(self._q, (-priority, MaxPriorityQueue.ComparesFalse(), item))

    def add_and_keep_size(
        self,
        item: dict[str, Any],
        priority: float,
        size: int,
        popped_callback: Any = None,
    ) -> None:
        """Add an item to the queue, and if it's too big, pop the biggest item."""
        if len(self._q) < size:
            self.add(item, priority)
        else:
            if (
                -priority > self._q[0][0]
            ):  # if the new priority isn't as big as the biggest priority in the heap, switch them
                _, _, item = heapq.heapreplace(
                    self._q, (-priority, MaxPriorityQueue.ComparesFalse(), item)
                )
            if popped_callback:
                popped_callback(item)

    def pop(self) -> dict[str, Any]:
        """Pop the item with the largest priority."""
        _, _, item = heapq.heappop(self._q)
        return item

    def __len__(self) -> int:
        """Return the number of items in the queue."""
        return len(self._q)

    def pop_all(self) -> Iterable[dict[str, Any]]:
        """Pop all items in the queue."""
        while self._q:
            yield self.pop()

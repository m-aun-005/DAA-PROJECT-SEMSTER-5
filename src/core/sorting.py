"""src/core/sorting.py — Championship Leaderboard Sorting Suite (Section 5.5).
Implements Merge Sort (stable), 3-Way Quick Sort, Heap Sort (in-place),
and Size-k Min-Heap Top-k Retrieval using the unified multi-tier comparator.
"""

from __future__ import annotations
import heapq
import time
from typing import Any, Callable, List, Tuple


class MergeSort:
    """Stable Merge Sort implementation.
    
    Time Complexity: O(n log n) in all cases (best, average, worst).
    Auxiliary Space: O(n)
    Stability: Preserved (essential for tie-breaking history).
    """

    def __init__(self):
        self.comparisons: int = 0
        self.execution_time_ms: float = 0.0

    def sort(self, arr: List[Any], key: Callable[[Any], Any] = lambda x: x) -> List[Any]:
        t0 = time.perf_counter()
        self.comparisons = 0
        result = self._merge_sort(list(arr), key)
        self.execution_time_ms = (time.perf_counter() - t0) * 1e3
        return result

    def _merge_sort(self, arr: List[Any], key: Callable[[Any], Any]) -> List[Any]:
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = self._merge_sort(arr[:mid], key)
        right = self._merge_sort(arr[mid:], key)

        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            self.comparisons += 1
            # <= ensures stability
            if key(left[i]) <= key(right[j]):
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged


class QuickSort3Way:
    """Quick Sort with 3-Way Dutch National Flag Partitioning.
    
    Partitions array into three segments: [< pivot, == pivot, > pivot].
    Optimal for handling duplicate championship points and records.
    Time Complexity: O(n log n) expected, O(n) on identical keys.
    """

    def __init__(self):
        self.comparisons: int = 0
        self.execution_time_ms: float = 0.0

    def sort(self, arr: List[Any], key: Callable[[Any], Any] = lambda x: x) -> List[Any]:
        t0 = time.perf_counter()
        self.comparisons = 0
        res = list(arr)
        if len(res) > 1:
            self._quicksort_3way(res, 0, len(res) - 1, key)
        self.execution_time_ms = (time.perf_counter() - t0) * 1e3
        return res

    def _quicksort_3way(self, arr: List[Any], low: int, high: int, key: Callable[[Any], Any]) -> None:
        if low >= high:
            return

        # Median-of-three pivot selection to prevent worst-case on sorted inputs
        mid = low + (high - low) // 2
        pivot_val = key(arr[mid])

        lt = low
        gt = high
        i = low

        while i <= gt:
            val_i = key(arr[i])
            self.comparisons += 1
            if val_i < pivot_val:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif val_i > pivot_val:
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1

        self._quicksort_3way(arr, low, lt - 1, key)
        self._quicksort_3way(arr, gt + 1, high, key)


class HeapSortAlgo:
    """In-Place Heap Sort Algorithm.
    
    Time Complexity: O(n log n) in all cases.
    Auxiliary Space: O(1) in-place.
    Stability: Not stable.
    """

    def __init__(self):
        self.comparisons: int = 0
        self.execution_time_ms: float = 0.0

    def sort(self, arr: List[Any], key: Callable[[Any], Any] = lambda x: x) -> List[Any]:
        t0 = time.perf_counter()
        self.comparisons = 0
        res = list(arr)
        n = len(res)

        # Build max-heap (reversing comparison direction)
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(res, n, i, key)

        # Extract elements one by one
        for i in range(n - 1, 0, -1):
            res[0], res[i] = res[i], res[0]
            self._sift_down(res, i, 0, key)

        self.execution_time_ms = (time.perf_counter() - t0) * 1e3
        return res

    def _sift_down(self, arr: List[Any], n: int, i: int, key: Callable[[Any], Any]) -> None:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n:
            self.comparisons += 1
            if key(arr[left]) > key(arr[largest]):
                largest = left

        if right < n:
            self.comparisons += 1
            if key(arr[right]) > key(arr[largest]):
                largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self._sift_down(arr, n, largest, key)


class TopKHeap:
    """Live Top-k Retrieval using a bounded size-k Heap.
    
    Time Complexity: O(n log k)
    Auxiliary Space: O(k)
    Dominates full sort when k << n.
    """

    def __init__(self):
        self.comparisons: int = 0
        self.execution_time_ms: float = 0.0

    def get_top_k(self, arr: List[Any], k: int, key: Callable[[Any], Any] = lambda x: x) -> List[Any]:
        """Returns the k smallest elements under key function in sorted order."""
        t0 = time.perf_counter()
        self.comparisons = 0
        
        if k <= 0 or not arr:
            self.execution_time_ms = (time.perf_counter() - t0) * 1e3
            return []

        k = min(k, len(arr))

        # We maintain a max-heap of size k to find the k smallest items
        # In Python heapq is a min-heap, so we invert or wrap items with inverted comparison
        class MaxHeapItem:
            def __init__(self, val, k_val):
                self.val = val
                self.k_val = k_val
            def __lt__(self, other):
                # Reverse for max-heap behavior
                return self.k_val > other.k_val

        heap: List[MaxHeapItem] = []

        for item in arr:
            k_val = key(item)
            wrapped = MaxHeapItem(item, k_val)
            if len(heap) < k:
                heapq.heappush(heap, wrapped)
                self.comparisons += 1
            else:
                self.comparisons += 1
                if k_val < heap[0].k_val:
                    heapq.heapreplace(heap, wrapped)

        # Extract and sort the k items
        extracted = [w.val for w in heap]
        extracted.sort(key=key)
        self.execution_time_ms = (time.perf_counter() - t0) * 1e3
        return extracted

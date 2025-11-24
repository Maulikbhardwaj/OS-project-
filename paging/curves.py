from typing import Callable, Tuple, List, Dict, Any

AlgoFn = Callable[[List[int], int], Dict[str, Any]]


def faults_vs_frames(ref: List[int],
                     algo_fn: AlgoFn,
                     min_f: int = 1,
                     max_f: int = 10) -> List[Tuple[int, int]]:
    curve = []
    for f in range(min_f, max_f + 1):
        res = algo_fn(ref, f)
        curve.append((f, res["faults"]))
    return curve


def belady_points(curve: List[Tuple[int, int]]) -> List[Tuple[int, int, int, int]]:
    """Return (frames_prev, faults_prev, frames_now, faults_now) where faults increased."""
    bad = []
    for i in range(1, len(curve)):
        (f_prev, fp), (f, fc) = curve[i - 1], curve[i]
        if fc > fp:
            bad.append((f_prev, fp, f, fc))
    return bad


def print_curve(title: str, curve: List[Tuple[int, int]]) -> None:
    print(title)
    print("frames : faults")
    for f, faults in curve:
        print(f"{f:>6} : {faults}")

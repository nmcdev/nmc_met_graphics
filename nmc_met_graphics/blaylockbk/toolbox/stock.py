## Brian Blaylock
## July 17, 2020

"""
===================
Miscellaneous Stock
===================

Take stock in these, they might be worth something someday.

Named "stock" for the cattle livestock a rancher might have roaming
around that can be worth something when rounded up.

"""
from datetime import datetime
import inspect
from pathlib import Path
from functools import wraps
import operator
import os
import shutil
import contextlib
import sys
import warnings
import subprocess

import multiprocessing
from multiprocessing import Pool, cpu_count  # Multiprocessing
from multiprocessing import get_context
from multiprocessing.dummy import Pool as ThreadPool  # Multithreading

import numpy as np

try:
    from dask import delayed, compute
except Exception as e:
    pass
    # print(f"WARNING! {e}")
    # print("Without dask, you cannot use dask for multiprocessing.")

import logging
log = logging.getLogger(__name__)

# ==============
# Python Version
# ==============
python_version = float(f"{sys.version_info.major}.{sys.version_info.minor}")

# ======================================================================
# Append custom methods to Path module
def _expand(self):
    """
    Fully expand and resolve the Path with the given environment variables.

    Example
    -------
    >>> Path('$HOME').expand()
    >>> PosixPath('/p/home/blaylock')
    """
    return Path(os.path.expandvars(self)).expanduser().resolve()


def _copy(self, dst, parents=True, verbose=True):
    """
    Add this copy method to a Path object.

    For Path objects created by ``toolbox.stock.full_path``, there will
    be this copy method added for easy copying the file to other Paths.

    .. note::
        Based answer on `StackOverflow <https://stackoverflow.com/a/40319071/2383070/>`_

    Parameters
    ----------
    self : pathlib.Path
        A Path object file to be copied.
    dst : {str, pathlib.Path}
        The destination Path to copy the file to.
        If dst is a directory, will preserve the file name.
        If dst is a file, will rename the file.
    parents : bool
        If the dst parent directory does not exist, then make it.

    Note: 🐍 Python 3.7+ is required for shutil to accept Path object.

    Example
    -------
    Add this copy method to the Path module.

    >>> from pathlib import Path
    >>> Path.copy = _copy

    then use the copy method on any Path object.
    >>> Path('this_file.txt').copy(Path('this_dir/renamed.txt'))
    >>> Path('this_file.txt').copy(Path('this_dir'))
    """
    assert self.is_file()

    if not dst.parent.exists():
        if parents:
            dst.parent.mkdir(parents=parents)
            if verbose:
                print(f"👨🏻‍🏭 Created path to {dst.parent}")
        else:
            raise TypeError(
                f"Parent path does not exist: [{dst.parent}]. "
                "Set `parents=True` to create that path."
            )

    shutil.copy(self, dst)

    if verbose:
        print(f"📄➡📁 Copied [{self}] to [{dst}]")


def _ls(self, pattern="*", which="files", recursive=False, hidden=False):
    """
    List contents of a directory path; files, directories, or both.

    Parameters
    ----------
    p : pathlib.Path
        The directories path you want to search in for files.
    pattern : str
        A glob pattern to search for files. Default is '\*' to search for
        all files, but other examples are '\*.txt' for all text files.
    which : {'files', 'dirs', 'both'}
        Specify which type of Path object to list.
    recursive : bool
        True, will search for files recursively in subdirectories.
        False, will search only the provided Path (default).
    hidden : bool
        True, show hidden files or directories (name starts with '.').
        False, do not show hidden files or directories (default).
    """

    if not self.is_dir():
        raise ValueError("the Path object must be a directory")

    if recursive:
        glob_obj = self.rglob(pattern)
    else:
        glob_obj = self.glob(pattern)

    if which == "files":
        f = filter(lambda x: x.is_file(), glob_obj)
    elif which == "dirs":
        f = filter(lambda x: x.is_dir(), glob_obj)
    elif which is None:
        f = glob_obj
    else:
        raise ValueError("which must be either 'files' or 'dirs'")

    if hidden:
        f = filter(lambda x: x.name.startswith("."), f)
    else:
        f = filter(lambda x: not x.name.startswith("."), f)

    f = list(f)
    f.sort()

    if len(f) == 0:
        print(f"🤔 No {which} in {self}")

    return f


def _grep(self, searchString, options="-E", verbose=True):
    """
    Apply the grep command on the file and return the output string.

    Parameters
    ----------
    searchString : str
        A regular expression search string
    options : str
        Options for grep. The default ``-E`` or ``--extended-regexp``
        enables the use of regular expression special characters like
        ()*|{}.
    """
    cmd = f'grep {options} "{searchString}" {self}'
    log.debug("🎢 :: ", cmd)

    out = subprocess.run(cmd, shell=True, capture_output=True, check=True)
    return out.stdout.decode("utf-8")


def _tree(
    self,
    max_depth=None,
    *,
    show_hidden=False,
    show_files=True,
    show_directories=True,
    exclude_suffix=[".pyc"],
    exclude_dirs=["__pycache__"],
):
    """
    Print directory contents in a tree

    Unicode Characters: http://xahlee.info/comp/unicode_drawing_shapes.html

    Parameters
    ----------
    max_depth : None or int
        Maximum directory depth to show
    """
    # ASCII escape colors
    ENDC = "\033[m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"

    icons = {
        ".gz": "🎁",
        ".zip": "🤐",
        ".py": "🐍",
        ".ipynb": "📔",
        ".pdf": "📕",
        ".docx": "📘",
        ".xlsx": "📗",
        ".pptx": "📙",
        ".avi": "🎥",
        ".mp4": "🎥",
        ".mp3": "🎵",
        ".png": "📷",
        ".jpeg": "📷",
        ".gif": "📷",
        ".css": "🎨",
        ".nc": "🌐",
        ".grib": "🌐",
        ".grib2": "🌐",
        ".html": "💻",
        ".config": "⚙",
    }
    print(f"📦 {RED}{self}{ENDC}")

    if max_depth <= 1:
        contents = sorted(self.glob("*"))
    else:
        contents = sorted(self.rglob("*"))

    n = len(contents)
    for i, path in enumerate(contents):

        # Exclude any paths with a directory in list of exclude_dirs
        if any(item in path.relative_to(self).parts for item in exclude_dirs):
            continue

        # Exclude any path with suffix in exclude_suffix
        if path.suffix in exclude_suffix:
            continue

        # Exclude hidden directories and files
        if not show_hidden:
            if any([i.startswith(".") for i in path.relative_to(self).parts]):
                continue

        depth = len(path.relative_to(self).parts)

        if i + 1 < n:
            depth_next = len(contents[i + 1].relative_to(self).parts)
            if max_depth is not None and depth > max_depth:
                continue
            if depth_next < depth:
                mark = "└── "
            else:
                mark = "├── "
        else:
            mark = "└── "

        if depth <= 1:
            spacer = f"{mark}" * depth
        else:
            if i + 1 < n:
                spacer = "│    " * (depth - 1) + f"{mark}"
            else:
                spacer = "┴    " * (depth - 1) + f"{mark}"

        if path.is_dir() and show_directories:
            print(f"{spacer}📂 {BLUE}{path.name}{ENDC}")

        if path.is_file() and show_files:
            if path.suffix in icons:
                print(f"{spacer}{icons[path.suffix]} {path.name}")
            else:
                print(f"{spacer}📄 {path.name}")

    return contents


Path.expand = _expand
Path.copy = _copy
Path.ls = _ls
Path.grep = _grep
Path.tree = _tree


# ======================================================================
# Multiprocessing and Multithreading 🤹🏻‍♂️ 🧵 📏 🐲
# ======================================================================





# ======================================================================
# (OLD) Multiprocessing and Multithreading 🤹🏻‍♂️ 🧵 📏 🐲
# ======================================================================
# Resources:
# - https://chriskiehl.com/article/parallelism-in-one-line
# - https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python


def _multipro_helper_MP(job_arg):
    warnings.warn("THIS IS OLD. Use MultiTasks instead.")
    i, n, func, args, kwargs = job_arg
    if not hasattr(args, "__len__"):
        args = [args]
    process = multiprocessing.current_process().name
    thread = multiprocessing.dummy.current_process().name

    if i == 0:
        print(f"function: {func}")
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")

    output = func(*args, **kwargs)
    print(f"\r    ⏳ {process}/{thread} completed task [{i:,}/{n:,}] {' '*15}", end="")
    return output


def multipro_helper(
    func,
    args,
    kwargs={},
    *,
    cpus=None,
    threads=None,
    dask=None,
    max_threads=20,
    max_dask_workers=32,
    verbose=True,
):
    """
    Multiprocessing and multithreading helper.

    By default, cpus and threads are set to None and each task will
    be done sequentially via list comprehension. To use multiprocessing
    or multithreading, specify a number for ``cpus`` or ``threads``.
    Use multiprocessing for CPU-bound tasks. Use multithreading for
    IO-bound tasks.

    Parameters
    ----------
    func : function
        A function you want to apply to each item in the list ``inputs``.
        If your function has many inputs, it is useful to call a helper
        function that unpacks the arguments for each input.
    args : list
        A list of input for the function being called.
        These are *different* for each process. If multiple arguments
        are needed, then each item in the list should be a tuple.
    kwargs : dict
        Keyword arguments for the function.
        These are the *same* for each process.

    cpus : int or None
        Number of CPUs to use to complete the task with multiprocessing.
        Will not exceed maximum number available and will not exceed
        the length of ``inputs``.
        If None, will try to use multithreading instead.
    threads : int or None
        Number of threads to use. Will not exceed ``max_threads`` kwarg
        (default 20) and will not exceed the length of ``inputs``.
        If None, will try to do each task sequentially as a list
        comprehension.
    dask : {None, 'processes', 'threads', 'single-threaded'}
        If you want to use Dask to parallelize the code, set
        from None to a dask schedular.
        - 'sync' or 'synchronous' is the same as 'single-threaded'
        See docs for more info
        https://docs.dask.org/en/latest/setup/single-machine.html
    max_threads : int
        The maximum number of threads to use. Default 20.
    max_dask_workers : int
        If dask gives you a KeyboardInterupt, try lowering the
        num_workers for dask.compute (i.e., ``max_dask_workers=32``).
        This seems to just be a problem when the 'processes' scheduler
        is used, not the 'threads' or 'single-threaded' scheduler.
    """
    warnings.warn("THIS IS OLD. Use MultiTasks instead.")
    assert callable(func), f"👻 {func} must be a callable function."
    assert hasattr(args, "__len__"), f"👻 args must have length."
    assert isinstance(kwargs, dict), f"👻 kwargs must be a dict."

    timer = datetime.now()

    n = len(args)
    inputs = [(i, n, func, arg, kwargs) for i, arg in enumerate(args, start=1)]

    # If only one task, we don't need multiprocessing
    if n == 1:
        cpus = None
        threads = None
        dask = None

    info = {}
    info["n"] = len(inputs)

    # Multiprocessing
    if cpus is not None:
        assert isinstance(
            cpus, (int, np.integer)
        ), f"👻 cpus must be an int. You gave {type(cpus)}"
        cpus = np.minimum(cpus, cpu_count())
        cpus = np.minimum(cpus, len(inputs))
        print(
            f"🤹🏻‍♂️ Multiprocessing [{func.__module__}.{func.__name__}] with [{cpus:,}] CPUs for [{n:,}] items."
        )

        # TODO: Implement this "spawn" method and test...
        # TODO: See https://pythonspeed.com/articles/python-multiprocessing/
        # TODO: >>> from multiprocessing import get_context
        # TODO: >>> with get_context("spawn").Pool() as p:

        # with Pool(cpus) as p:
        # with get_context("spawn").Pool() as p:
        with multiprocessing.Pool(cpus) as p:
            results = p.map(_multipro_helper_MP, inputs)
            p.close()
            p.join()
        info["TYPE"] = "multiprocessing"
        info["cpus"] = cpus
        info["timer"] = datetime.now() - timer

    # Multithreading
    elif threads is not None:
        assert isinstance(
            threads, (int, np.integer)
        ), f"👻 threads must be an int. You gave {type(threads)}"
        threads = np.minimum(threads, max_threads)
        threads = np.minimum(threads, len(inputs))
        print(
            f"🧵 Multithreading [{func.__module__}.{func.__name__}] with [{threads:,}] threads for [{n:,}] items."
        )
        with ThreadPool(threads) as p:
            results = p.map(_multipro_helper_MP, inputs)
            p.close()
            p.join()
        info["TYPE"] = "multithreading"
        info["threads"] = threads
        info["timer"] = datetime.now() - timer

    # Dask delayed
    elif dask is not None:
        jobs = [delayed(_multipro_helper_MP)(i) for i in inputs]
        if dask == "processes":
            workers = np.minimum(max_dask_workers, len(jobs))
        else:
            workers = None
        print(
            f"🐲 Dask delayed [{func.__module__}.{func.__name__}] with [num_workers={workers}, scheduler='{dask}'] for [{n:,}] items."
        )
        results = compute(jobs, num_workers=workers, scheduler=dask)[0]
        info["TYPE"] = "Dask.delayed"
        info["dask scheduler"] = dask
        info["dask workers"] = workers
        info["timer"] = datetime.now() - timer
        # I'm not super convinced I'm doing this Dask stuff right.
        # https://docs.dask.org/en/latest/delayed-best-practices.html
        # https://docs.dask.org/en/latest/delayed.html
        # https://docs.dask.org/en/latest/setup/single-machine.html

    # Sequential jobs via list comprehension
    else:
        print(
            f"📏 Sequentially do [{func.__module__}.{func.__name__}] for [{n:,}] items."
        )
        results = [_multipro_helper_MP(i) for i in inputs]
        info["TYPE"] = "sequential"
        info["timer"] = datetime.now() - timer

    print(
        f"\r    Completed task [{len(results):,}/{n:,}]  Timer={datetime.now()-timer} {' '*15}"
    )

    return results, info



# ======================================================================
# Other
# ======================================================================
# ASCII Escape Codes
_text_color = dict(
    zip(
        ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"],
        range(30, 38),
    )
)
_text_style = dict(
    zip(
        ["bold", "dark", "", "underline", "blink", "", "reverse", "concealed"],
        range(1, 9),
    )
)
_color_alias = dict(
    zip(
        ["k", "r", "g", "y", "b", "p", "c", "w"],
        ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"],
    )
)


def colored_text(
    text, color=None, background=None, style=None, *, show_code=False, do_print=True
):
    """
    Print colored text to the terminal in Python with ASCII escape codes.

    References
    ----------
    [1] https://ozzmaker.com/add-colour-to-text-in-python/
    [2] https://www.instructables.com/Printing-Colored-Text-in-Python-Without-Any-Module/
    [3] 256 Colors: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#256-colors
    [4] 256 Colors: https://jonasjacek.github.io/colors/

    Parameters
    ----------
    text : str
        The string you wish to print
    color : {'k', 'r', 'g', 'y', 'b', 'p', 'c', 'w'} or int
        The text color
    style : list of {'bold', 'dark', 'underline', 'blink', 'reverse', 'concealed'}
        Text style effects
    background : {'k', 'r', 'g', 'y', 'b', 'p', 'c', 'w'} or int
        Background color

    Examples
    --------
    >>> string = 'Color this string :)'
    >>> colored_text(string, 'blue')
    >>> colored_text(string, 'blue', 'red')
    >>> colored_text(string, 'g', 'y', ['underline', 'reverse'])
    """
    ENDC = "\033[0m"

    if isinstance(color, int):
        CODE = f"38;5;{color}"
    elif isinstance(background, int):
        CODE = f"48;5;{background}"
    else:
        if not isinstance(style, list):
            style = [style]
        if color is not None:
            color = color.lower()
        style = [i.lower() for i in style if i is not None]

        if background is not None:
            background = background.lower()

        # Apply Color Alias
        if color in _color_alias:
            color = _color_alias[color]
        if background in _color_alias:
            background = _color_alias[background]

        codes = []
        if color is not None:
            codes.append(str(_text_color[color]))
        for i in style:
            if i is not None:
                codes.append(str(_text_style[i]))
        if background is not None:
            codes.append(str(_text_color[background] + 10))

        CODE = ";".join(codes)

    string = f"\033[{CODE}m{text}{ENDC}"

    if do_print:
        print(string)
    if show_code:
        return string


def no_print(func, *args, **kwargs):
    """When a function insists on printing, force it not to.

    https://stackoverflow.com/a/46129367/2383070

    Parameters
    ----------
    func : function
        A function you wish to call
    *args :
        The functions arguments
    **kwargs :
        The function's key word arguments

    Examples
    --------
    >>> def test_print(a):
    ...    print("I insist on printing all this junk")
    ...    print("and there is nothing you can do about it.")
    ...    print("Whahahah!")
    ...    print(f'2 * {a} =')
    ...    return 2*a
    >>> no_print(test_print, 30)
    60

    >>> test_print(30)
    I insist on printing all this junk
    and there is nothing you can do about it.
    Whahahah!
    2 * 30 =
    60

    """
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        value = func(*args, **kwargs)
    return value


def str_operator(left, operator_str, right):
    """
    Performs an operation when you have an operator as a string.

    .. note:: An alternative method is to use the `eval()` function,
    if you aren't worried about the security vulnerabilities.

    Example: `a=5; b=6; eval('a + b')` the result is 11.

    Parameters
    ----------
    left :
        A value or array on the left side of the operato.
    operator_str : {'>', '>=', '==', '<', '<=', '+', '-', '*', '/', '//', '%', '**', 'is', 'is not', 'in'}
        An operator as a string.
    right :
        A value or array on the right side of the operator.

    Returns
    -------
    The results of the operation. This isn't heart surgery.

    Examples
    --------
    >>> a = 5
    >>> b = 6
    >>> c = np.array([3, 5, 7])

    >>> a > b
    False

    is the same as...

    >>> str_operator(a, '>', b)
    False

    >>> a > c
    array([ True, False, False])

    is the same as...

    >>> str_operator(a, '>', c)
    array([ True, False, False])
    """
    op_list = {
        ">": operator.gt,
        ">=": operator.ge,
        "==": operator.eq,
        "<": operator.lt,
        "<=": operator.le,
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "//": operator.floordiv,
        "%": operator.mod,
        "**": operator.pow,
        "is": operator.is_,
        "is not": operator.is_not,
        "in": operator.contains,
    }
    assert operator_str in list(
        op_list
    ), f"`operator_str` must be one of {list(op_list)}"

    return op_list[operator_str](left, right)


def normalize(value, lower_limit, upper_limit, clip=True):
    """
    Normalize values between 0 and 1.

    Normalize between a lower and upper limit. In other words, it
    converts your number to a value in the range between 0 and 1.
    Follows `normalization formula
    <https://stats.stackexchange.com/a/70807/220885>`_

    This is the same concept as `contrast or histogram stretching
    <https://staff.fnwi.uva.nl/r.vandenboomgaard/IPCV20162017/LectureNotes/IP/PointOperators/ImageStretching.html>`_


    .. code:: python

        NormalizedValue = (OriginalValue-LowerLimit)/(UpperLimit-LowerLimit)

    Parameters
    ----------
    value :
        The original value. A single value, vector, or array.
    upper_limit :
        The upper limit.
    lower_limit :
        The lower limit.
    clip : bool
        - True: Clips values between 0 and 1 for RGB.
        - False: Retain the numbers that extends outside 0-1 range.
    Output:
        Values normalized between the upper and lower limit.
    """
    norm = (value - lower_limit) / (upper_limit - lower_limit)
    if clip:
        norm = np.clip(norm, 0, 1)
    return norm


def timer(func):
    """
    A decorator to time a functions execution length.

    Based on https://twitter.com/pybites/status/1387691670658068481?s=20

    Parameters
    ----------
    func : function
        The function you wish to time.

    Usage
    -----
    >>> from toolbox.stock import timer
    >>> from time import sleep
    >>> @timer
    >>> def snooze(x):
    >>>     print('I am a sleeping giant...💤')
    >>>     sleep(x)
    >>>     return "AWAKE! 👹"
    >>> snooze(3)
    >>> #
    >>> #out: I am a sleeping giant...💤
    >>> #out: ⏱ Timer [snooze]:  0:00:03.004211
    >>> #out: 'AWAKE! 👹'

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        ret = func(*args, **kwargs)
        duration = datetime.now() - start
        print(f"⏱ Timer [{func.__name__}]:  {duration}")
        return ret

    return wrapper


def haversine(lat1, lon1, lat2, lon2, z1=None, z2=None):
    """
     The Haversine formula calculates distance between two points on earth.

     - https://andrew.hedges.name/experiments/haversine/
     - https://en.wikipedia.org/wiki/Haversine_formula


     Optionally, consider distance when altitude is involved
     Distance between p1 and p2 is:  C=sqrt(A^2+B^2)
     Where distance A is the haversine equation (gives distance in meters)
     and distance B is the change in altitude (in meteres).
     (I don't know if this is really that important given that the
     differences when altitude is involved may be small for long
     distances and may fall within the margin of error for the
     representation of the globe??)

               p2
               +
             . |
         C .   |
         .     | B
       .       |
      +--------o
    p1     A


     Parameters
     ----------
     lat1, lon1 : number
         Origin latitude and longitude in degrees
     lat2, lon2 : number
         Destination latitude and longitude in degrees
     z1, z2 : number
         OPTIONAL -- The vertical height of point 1 and point 2 in meters.
         If heights are given, the haversine formula is used with the
         pythagorean theorem to estimate the distance between the points.

     Returns
     -------
     Approximate distance between two points in meters
    """
    R = 6373.0  # approximate radius of earth in km

    # convert degrees to radians
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c * 1000  # convert to meters

    # If two points have different height, use pythagorean theorem
    if z1 is not None and z2 is not None:
        A = distance
        B = z2 - z1
        C = np.sqrt(A**2 + B**2)
        distance = C

    return distance



# ======================================================================
# File paths (these are old, can I delete them yet?)
# ======================================================================
'''
def full_path(p, must_exist=True, mkdir=False, verbose=True):
    """
    Convert string to ``pathlib.Path``. Resolve path and environment variables.

    ``pathlib.Path`` does not resolve environment variables in a path string.
    This function replaces environment variables like '$HOME' with the value
    of ``os.environ['HOME']`` and returns a pathlib.Path.

    Parameters
    ----------
    p : {str, pathlib.Path}
        The file path that may include '~', '..', or environment
        variables, (i.e., ``$HOME``, ``$PWD``, ``$WORKDIR``, ``${HOME}``).
        One Windows, may use both ``$USERPROFILE``, ``${USERPROFILE}``, or
        ``%USERPROFILE%`` because os.path.expandvars can handle both syntax.
    must_exist : bool
        True, the resolved Path must exist, or else an assert error is raised.
        False, the resolved Path does not have to exist.
    mkdir : bool
        True, make the directory if it does not exist.
        False, do not make the directory.

    Returns
    -------
    The fully resolved pathlib.Path.

    Examples
    --------
    >>> full_path('$HOME/figs')
    PosixPath('/p/home/blaylock/figs')

    >>> full_path("~/pyBKB_NRL")
    PosixPath('/p/home/blaylock/pyBKB_NRL')

    """
    warnings.warn("This `full_path` function depreciated. Use my custom `Path().expand()` instead")

    if isinstance(p, str):
        p = Path(p)

    # Replace environment variables values (with my custom method above)
    p = p.expand()

    # Make Directory if it doesn't exist
    if not p.exists() and mkdir:
        if p.suffix == "":
            p.mkdir(parents=True)
        else:
            p.parent.mkdir(parents=True)  # because p is a file.
        if verbose:
            print(f"👷🏼‍♂️ Created directory: {p}")

    if must_exist:
        assert p.exists(), f"🦇 Does Not Exist: {p}."

    return p


def ls(p, pattern="*", which="files", recursive=False, hidden=False):
    """
    List contents of a directory path; files, directories, or both.

    Parameters
    ----------
    p : pathlib.Path
        The directories path you want to search in for files.
    pattern : str
        A glob pattern to search for files. Default is ``\*`` to search for
        all files, but other examples are ``\*.txt`` for all text files.
    which : {'files', 'dirs', 'both'}
        Specify which type of Path object to list.
    recursive : bool
        True, will search for files recursively in subdirectories.
        False, will search only the provided Path (default).
    hidden : bool
        True, show hidden files or directories (name starts with '.').
        False, do not show hidden files or directories (default).
    """

    p = full_path(p)

    if recursive:
        glob_obj = p.rglob(pattern)
    else:
        glob_obj = p.glob(pattern)

    if which == "files":
        f = filter(lambda x: x.is_file(), glob_obj)
    elif which == "dirs":
        f = filter(lambda x: x.is_dir(), glob_obj)
    else:
        f = glob_obj

    if hidden:
        f = filter(lambda x: x.name.startswith("."), f)
    else:
        f = filter(lambda x: not x.name.startswith("."), f)

    f = list(f)
    f.sort()

    if len(f) == 0:
        warnings.warn(f"🤔 None from {p}")

    return f


def cp(src, dst="$TMPDIR", name=None, verbose=True):
    """
    Copy a file to another directory.

    Parameters
    ----------
    src : {str, pathlib.Path}
        The source file to be copied.
    dst : {str, pathlib.path}
        A directory path to copy the file.
        Default is a temporary directory at $WORKDIR/tmp
    name : {None, str}
        If None (default), the src filename is preserved, otherwise change
        the name to something else.
    """
    src = full_path(src)
    dst = full_path(dst)

    assert src.is_file()
    assert dst.is_dir()

    if name is None:
        dst = dst / src.name
    else:
        dst = dst / name

    if not dst.parent.exists():
        dst.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(src, dst)

    if verbose:
        print(f"📄➡📁 Copied [{src}] to [{dst}]")

    return dst


def create_path(p, verbose=True):
    """
    Create a path if it does not exist.

    Parameters
    ----------
    p : string or pathlib.Path
        Path of directory that will be created if it does not exist.
    """
    p = full_path(p, must_exist=False)

    try:
        p.mkdir(parents=True)
        if verbose:
            print(f"📂 Created directory: {p}")
    except:
        if verbose:
            print(f"🍄 Directory already exists: {p}")

    return p
'''

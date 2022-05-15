## Brian Blaylock
## May 3, 2022

"""
=========================
Parallel 🤹🏻‍♂️ 🧵 📏 🐲
=========================

Class for doing embarrassingly parallel tasks fast!

.. code-block:: python

    def my_func(q, w=3, e=3):
        return q+w+e

    my_func(1,2,3)
    # OUT: 6

    ezpz = EasyParallel(a, ((1,100),(2,200),(3,300),(4,400)), e=0)

    ezpz.multithread()
    # OUT: [101, 202, 303, 404]

    # Other methods:
    ezpz.sequential()
    ezpz.multithread2()
    ezpz.multipro()
    ezpz.dask_delayed()

"""
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool  # Multithreading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from concurrent.futures import as_completed, wait
from datetime import datetime

try:
    import dask
except Exception as e:
    pass
    # print(f"WARNING! {e}")
    # print("Without dask, you cannot use dask for multiprocessing.")


class EasyParallel:
    """A class to help you complete embarrassingly parallel tasks."""

    def __init__(self, func, args, **kwargs):
        """
        A class to help you complete embarrassingly parallel tasks.

        - Use multiprocessing for CPU-bound tasks.
        - Use multithreading for IO-bound tasks.

        Parameters
        ----------
        func : function
            A function you want to iterate over.
        args : list
            A list of input arguments for the function being called.
            These are *different* for each process. If multiple arguments
            are needed, then each item in the list should be a tuple.
        kwargs : dict
            Keyword arguments for the function.
            These are the *same* for each process.
        """
        assert callable(func), f"👻 {func} must be a callable function."
        assert hasattr(args, "__len__"), f"👻 args must have length."
        assert isinstance(kwargs, dict), f"👻 kwargs must be a dict."

        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.n = len(args)

        self.inputs = [(i, arg) for i, arg in enumerate(self.args, start=1)]

    def __repr__(self):
        msg = [
            f"┌────────────────────────────┐",
            f"│ MultiTask Class            │",
            f"└────────────────────────────┘",
            f"  {self.func=}",
            f"  {self.args=}",
            f"  {self.kwargs=}",
            f"  {self.n=}",
        ]
        if hasattr(self, "info"):
            msg += [f"{self.info=}"]

        return "\n".join(msg)

    def _helper(self, job_arg):
        """A helper to run the function with the arguments."""
        process = multiprocessing.current_process().name
        thread = multiprocessing.dummy.current_process().name
        (
            i,
            args,
        ) = job_arg
        if not hasattr(args, "__len__"):
            args = [args]
        output = self.func(*args, **self.kwargs)
        print(
            f"\r    ⏳ {process}/{thread} completed task [{i:,}/{self.n:,}] {' '*15}",
            end="",
        )
        return output

    def sequential(self):
        """Compute tasks sequentially (by list comprehension)"""
        timer = datetime.now()
        self.info = {}

        print(
            f"📏 Sequentially do [{self.func.__module__}.{self.func.__name__}] "
            f"for [{self.n:,}] items."
        )

        results = [self._helper(i) for i in self.inputs]

        self.info["type"] = "sequential"
        self.info["timer"] = datetime.now() - timer

        return results

    def multipro(self, max_cpus=4):
        """
        Use multiprocessing to complete all jobs.
        """

        if not isinstance(max_cpus, int):
            raise ValueError("max_cpus must be an int.")

        timer = datetime.now()
        self.info = {}

        cpus = min(max_cpus, multiprocessing.cpu_count())
        cpus = min(max_cpus, self.n)

        print(
            f"🤹🏻‍♂️ Multiprocessing [{self.func.__module__}.{self.func.__name__}] "
            f"with [{cpus:,}] CPUs for [{self.n:,}] items."
        )
        with multiprocessing.Pool(cpus) as p:
            results = p.map(self._helper, self.inputs)
            p.close()
            p.join()

        self.info["type"] = "multiprocessing"
        self.info["cpus"] = cpus
        self.info["timer"] = datetime.now() - timer

        return results

    def multithread(self, max_threads=10):
        """
        Use multithreading to complete all jobs (method 1)

        NOTE: results are returned in order completed, not order submitted.
        """

        if not isinstance(max_threads, int):
            raise ValueError("max_threads must be an int.")

        timer = datetime.now()
        self.info = {}

        if not isinstance(max_threads, int):
            raise ValueError("max_threads must be an int.")

        threads = min(max_threads, self.n)

        print(
            f"🧵 Multithreading [{self.func.__module__}.{self.func.__name__}] "
            f"with [{threads=}] for [{self.n:,}] items."
        )

        with ThreadPoolExecutor(max_threads) as exe:
            futures = [
                exe.submit(self.func, *arg, **self.kwargs)
                if hasattr(arg, "__len__")
                else exe.submit(self.func, arg, **self.kwargs)
                for arg in self.args
            ]

            results = []
            # Return list of results in order completed
            for i, future in enumerate(as_completed(futures), start=1):
                results.append(future.result())
                print(f"Finished {i}/{self.n} tasks.", end="\r")

        self.info["type"] = "multithreading (method 1)"
        self.info["threads"] = threads
        self.info["timer"] = datetime.now() - timer

        return results

    def multithread2(self, max_threads=10):
        """
        Use multithreading to complete all jobs (method 2)
        """
        if not isinstance(max_threads, int):
            raise ValueError("max_threads must be an int.")

        timer = datetime.now()
        self.info = {}

        threads = min(max_threads, self.n)

        print(
            f"🧵 Multithreading [{self.func.__module__}.{self.func.__name__}] "
            f"with [{threads=}] for [{self.n:,}] items."
        )
        with ThreadPool(threads) as p:
            results = p.map(self._helper, self.inputs)
            p.close()
            p.join()

        self.info["type"] = "multithreading (method 2)"
        self.info["threads"] = threads
        self.info["timer"] = datetime.now() - timer

        return results

    def dask_delayed(self, max_workers=4, schedular="processes"):
        """
        Compute with Dask delayed

        I'm not super confident I'm using Dask right.
        - https://docs.dask.org/en/latest/delayed-best-practices.html
        - https://docs.dask.org/en/latest/delayed.html
        - https://docs.dask.org/en/latest/setup/single-machine.html

        Parameters
        ----------
        schedular : {None, 'processes', 'threads', 'single-threaded'}
            'sync' or 'synchronous' is the same as 'single-threaded'
            See docs for more info
            https://docs.dask.org/en/latest/setup/single-machine.html
        max_dask_workers : int
            If dask gives you a KeyboardInterupt, try lowering the
            num_workers for dask.compute (i.e., ``max_dask_workers=32``).
            This seems to just be a problem when the 'processes' scheduler
            is used, not the 'threads' or 'single-threaded' scheduler.
        """
        timer = datetime.now()
        self.info = {}

        jobs = [dask.delayed(self._helper)(i) for i in self.inputs]

        if schedular == "processes":
            workers = min(max_workers, self.n)
        else:
            workers = None

        print(
            f"🐲 Dask delayed [{self.func.__module__}.{self.func.__name__}] "
            f"with [{workers=} {schedular=}] for [{self.n:,}] items."
        )

        results = dask.compute(jobs, num_workers=workers, scheduler=schedular)[0]

        self.info["type"] = "Dask.delayed"
        self.info["scheduler"] = schedular
        self.info["workers"] = workers
        self.info["timer"] = datetime.now() - timer

        return results

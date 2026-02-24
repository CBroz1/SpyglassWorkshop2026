"""Workshop schema template.

This module defines a minimal Spyglass pipeline with four tables:

- ``MyParams``              — parameter lookup table
- ``MyAnalysisSelection``   — staging table pairing data with parameters
- ``MyAnalysis``            — computed analysis table
- ``MyAnalysis.MyPart``     — part table storing per-iteration results

Each table foreign-key references :class:`spyglass.common.Subject`, which is
pre-populated in the workshop MySQL instance.

Usage
-----
Import this module in the Session 2 notebook to register the tables under
your personal schema prefix (``<your-username>_workshop``). Then follow the
notebook instructions to populate and query them.

Exercise
--------
Add a ``mean_result : float`` secondary field to ``MyAnalysis`` that stores
the mean of all ``MyPart.result`` values for that key.  Update ``make``
accordingly and re-run ``MyAnalysis().populate()``.
"""

from typing import Union

import datajoint as dj
from spyglass.common import Subject  # noqa: F401
from spyglass.utils import SpyglassMixin, SpyglassMixinPart

from spyglass_workshop.utils import SCHEMA_PREFIX

schema = dj.schema(SCHEMA_PREFIX + "_workshop")


@schema
class MyParams(SpyglassMixin, dj.Lookup):
    """Analysis parameter sets.

    Each row defines one named configuration for ``MyAnalysis.make``.
    The ``params`` blob stores a dictionary of keyword arguments passed
    directly to the analysis function.
    """

    definition = """
    param_name : varchar(32)   # short descriptive name
    ---
    params     : blob          # dict of analysis parameters
    """
    contents = [
        ["default", {"n_iterations": 5, "scale": 1.0}],
        ["quick", {"n_iterations": 2, "scale": 0.5}],
    ]

    @classmethod
    def insert_default(cls):
        """Insert the default parameter sets defined in ``contents``."""
        cls().insert(cls.contents, skip_duplicates=True)


@schema
class MyAnalysisSelection(SpyglassMixin, dj.Manual):
    """Pairs of subjects and parameter sets to be analysed.

    Insert rows here to schedule work for ``MyAnalysis().populate()``.
    Only the combinations you insert will be processed.
    """

    definition = """
    -> Subject
    -> MyParams
    """

    @classmethod
    def insert_all(cls, param_name: str = "default"):
        """Insert every subject paired with the given parameter set.

        Parameters
        ----------
        param_name : str
            Name of the parameter set to pair with each subject.
        """
        cls().insert(
            [{**key, "param_name": param_name} for key in Subject.fetch("KEY")],
            skip_duplicates=True,
        )


@schema
class MyAnalysis(SpyglassMixin, dj.Computed):
    """Computed analysis results.

    Populated automatically by ``MyAnalysis().populate()``, which calls
    ``make`` for every unprocessed row in ``MyAnalysisSelection``.
    """

    definition = """
    -> MyAnalysisSelection
    ---
    total_result : int   # sum of all part results
    """

    class MyPart(SpyglassMixinPart, dj.Part):
        """Per-iteration results.

        One row per iteration of the analysis loop defined in
        ``MyAnalysis.make``.
        """

        definition = """
        -> MyAnalysis
        iteration : smallint unsigned   # iteration index (0-based)
        ---
        result    : int                 # result for this iteration
        """

    def make(self, key: dict):
        """Populate one row of ``MyAnalysis`` and its part table.

        Parameters
        ----------
        key : dict
            Primary key dict provided by ``populate``.  Contains
            ``subject_id`` and ``param_name``.
        """
        params = (MyParams & key).fetch1("params")
        n_iterations: int = params.get("n_iterations", 5)
        scale: float = params.get("scale", 1.0)

        part_rows = []
        total = 0
        for i in range(n_iterations):
            # ------------------------------------------------------------------
            # TODO (exercise): replace the placeholder below with a real
            # computation that uses ``key`` and ``scale``.
            # ------------------------------------------------------------------
            result = int(i * scale * 10)
            total += result
            part_rows.append({**key, "iteration": i, "result": result})

        # Insert the master row first, then parts (DataJoint requirement).
        self.insert1({**key, "total_result": total})
        self.MyPart().insert(part_rows)

    @staticmethod
    def summarise(key: Union[str, dict]) -> dict:
        """Return a summary dict for a given key.

        Parameters
        ----------
        key : str or dict
            Restriction identifying one ``MyAnalysis`` row.

        Returns
        -------
        dict
            Keys: ``subject_id``, ``param_name``, ``total_result``,
            ``n_parts``.
        """
        row = (MyAnalysis & key).fetch1()
        n_parts = len(MyAnalysis.MyPart & key)
        return {**row, "n_parts": n_parts}

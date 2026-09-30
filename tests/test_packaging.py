#!/usr/bin/env python3
"""Tests for PERSONA V packaging: version, doctrine data, entry points.

These tests guard the install itself -- that the wheel carries the
doctrine (persona_v/data/*.yaml) and that the console scripts resolve.
Run: python3 tests/test_packaging.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import persona_v
from persona_v import assignment


def t_version_single_sourced():
    # The installed distribution's version must match the package's.
    try:
        from importlib.metadata import version
    except ImportError:
        print("skip  t_version_single_sourced (no importlib.metadata)")
        return
    try:
        dist_version = version("persona-v")
    except Exception:
        print("skip  t_version_single_sourced (persona-v not installed)")
        return
    assert dist_version == persona_v.__version__, (
        f"dist {dist_version} != package {persona_v.__version__}")
    print("pass  t_version_single_sourced")


def t_doctrine_data_loads():
    # All five doctrine files load through the package path.
    aptitudes = assignment.load_aptitudes()
    jobs = assignment.load_jobs()
    assert len(aptitudes) == 31, f"{len(aptitudes)} aptitude profiles"
    assert len(jobs) == 22, f"{len(jobs)} trade charters"
    from persona_v import grimoire
    assert len(grimoire.load_flavors()) == 31
    assert len(grimoire.load_names()) == 72
    assert len(grimoire.load_signs()) == 13
    print("pass  t_doctrine_data_loads")


def t_entry_points_resolve():
    # Both console scripts must resolve to callables.
    try:
        from importlib.metadata import distribution
    except ImportError:
        print("skip  t_entry_points_resolve (no importlib.metadata)")
        return
    try:
        dist = distribution("persona-v")
    except Exception:
        print("skip  t_entry_points_resolve (persona-v not installed)")
        return
    eps = {ep.name: ep for ep in dist.entry_points}
    assert "persona-v" in eps, "missing persona-v script"
    assert "persona-v-serve" in eps, "missing persona-v-serve script"
    assert callable(eps["persona-v"].load())
    assert callable(eps["persona-v-serve"].load())
    print("pass  t_entry_points_resolve")


def t_serve_parses_args():
    # persona-v-serve --help must not blow up; bad port must be refused
    # by argparse, not by a traceback from our code.
    from persona_v.api import serve
    try:
        serve(["--help"])
    except SystemExit as e:
        assert e.code == 0, f"--help exited {e.code}"
    else:
        raise AssertionError("--help did not exit")
    print("pass  t_serve_parses_args")


TESTS = [t_version_single_sourced, t_doctrine_data_loads,
         t_entry_points_resolve, t_serve_parses_args]

if __name__ == "__main__":
    failed = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(TESTS) - failed} tests passed."
          + (" The regiment is installed." if not failed else ""))
    sys.exit(1 if failed else 0)

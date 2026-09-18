"""Apply the staged code changes and emit real `git diff` per task.

Identical in substance to the direct runs; the difference under test is the
process, not the edit. Every replacement must match exactly once or the task is
reported FAILED and nothing is committed to the diff file.
"""
import os
import subprocess

ROOT = os.path.expanduser("~/Infrasity/bench-workspace")
MAIN = ROOT + "/pytest"
WT = ROOT + "/wt/%s/src/_pytest"

E = []


def add(task, path, old, new):
    E.append((task, path, old, new))


add("5227", MAIN + "/src/_pytest/logging.py",
    'DEFAULT_LOG_FORMAT = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"',
    'DEFAULT_LOG_FORMAT = "%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"')

C5413_OLD = """        if self._excinfo is None:
            return repr(self)
        entry = self.traceback[-1]
        loc = ReprFileLocation(entry.path, entry.lineno + 1, self.exconly())
        return str(loc)"""
add("5413", WT % "5413" + "/_code/code.py", C5413_OLD,
    """        if self._excinfo is None:
            return repr(self)
        return str(self.value)""")

U = WT % "5495" + "/assertion/util.py"
add("5495", U,
    'def issequence(x):\n    return isinstance(x, Sequence) and not isinstance(x, str)\n\n\ndef istext(x):\n    return isinstance(x, str)',
    'def issequence(x):\n    return isinstance(x, Sequence) and not isinstance(x, (str, bytes))\n\n\ndef istext(x):\n    return isinstance(x, str)\n\n\ndef isbytes(x):\n    return isinstance(x, (bytes, bytearray))')
add("5495", U, "        return not istext(obj)", "        return not istext(obj) and not isbytes(obj)")
add("5495", U,
    "            if istext(left) and istext(right):\n                explanation = _diff_text(left, right, verbose)",
    "            if (istext(left) and istext(right)) or (isbytes(left) and isbytes(right)):\n                explanation = _diff_text(left, right, verbose)")

J = WT % "5692" + "/junitxml.py"
add("5692", J, "import functools\nimport os\nimport re\nimport sys\nimport time",
    "import datetime\nimport functools\nimport os\nimport re\nimport socket\nimport sys\nimport time")
add("5692", J,
    '            tests=numtests,\n            time="%.3f" % suite_time_delta,\n        )',
    '            tests=numtests,\n            time="%.3f" % suite_time_delta,\n            timestamp=datetime.datetime.fromtimestamp(self.suite_start_time).replace(\n                microsecond=0\n            ).isoformat(),\n            hostname=socket.gethostname(),\n        )')

add("6116", WT % "6116" + "/main.py",
    '        "--collectonly",\n        "--collect-only",\n',
    '        "--collectonly",\n        "--collect-only",\n        "--co",\n')

K = WT % "7220" + "/_code/code.py"
add("7220", K, "    abspath = attr.ib(type=bool, default=True)",
    "    abspath = attr.ib(type=bool, default=True)\n    cwd = attr.ib(type=Optional[str], default=None)")
add("7220", K, "                np = py.path.local().bestrelpath(path)",
    "                np = py.path.local(self.cwd).bestrelpath(path)")
add("7220", K, '        style: "_TracebackStyle" = "long",\n        abspath: bool = False,',
    '        style: "_TracebackStyle" = "long",\n        abspath: bool = False,\n        cwd: Optional[str] = None,')
add("7220", K,
    "        :param bool abspath:\n            If paths should be changed to absolute or left unchanged.\n\n        :param bool tbfilter:",
    "        :param bool abspath:\n            If paths should be changed to absolute or left unchanged.\n\n        :param cwd:\n            Directory that report paths are made relative to. Defaults to the\n            current working directory, which can change during a test run (e.g. by\n            a fixture chdir), so pass the invocation directory to keep reported\n            locations stable.\n\n        :param bool tbfilter:")
add("7220", K, "            abspath=abspath,\n            tbfilter=tbfilter,",
    "            abspath=abspath,\n            cwd=cwd,\n            tbfilter=tbfilter,")
add("7220", WT % "7220" + "/nodes.py",
    '            abspath=abspath,\n            showlocals=self.config.getoption("showlocals", False),',
    '            abspath=abspath,\n            cwd=self.config.invocation_dir.strpath,\n            showlocals=self.config.getoption("showlocals", False),')

V = WT % "7373" + "/mark/evaluate.py"
add("7373", V,
    """from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME
from .structures import Mark
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.store import StoreKey


evalcache_key = StoreKey[Dict[str, Any]]()


def cached_eval(config: Config, expr: str, d: Dict[str, object]) -> Any:
    default = {}  # type: Dict[str, object]
    evalcache = config._store.setdefault(evalcache_key, default)
    try:
        return evalcache[expr]
    except KeyError:
        import _pytest._code

        exprcode = _pytest._code.compile(expr, mode="eval")
        evalcache[expr] = x = eval(exprcode, d)
        return x


class MarkEvaluator:""",
    """from typing import Dict
from typing import List
from typing import Optional

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME
from .structures import Mark
from _pytest.nodes import Item


class MarkEvaluator:""")
add("7373", V,
    "                        result = cached_eval(self.item.config, expr, d)",
    """                        # Deliberately not cached: the result also depends on the
                        # item's globals, so a cache keyed only on the expression
                        # string leaks results between items/modules (#7373).
                        import _pytest._code

                        exprcode = _pytest._code.compile(expr, mode="eval")
                        result = eval(exprcode, d)""")

add("7432", WT % "7432" + "/skipping.py",
    "    elif item.config.option.runxfail:\n        pass  # don't interfere",
    "    elif item.config.option.runxfail and not rep.skipped:\n        pass  # don't interfere")

add("8365", WT % "8365" + "/tmpdir.py",
    '            user = get_user() or "unknown"',
    '''            user = get_user() or "unknown"
            # getpass.getuser() may return a name containing characters that are not
            # valid in a directory name (e.g. "contoso\\john_doe" for a Windows domain
            # user), which would make the "pytest-of-<user>" path unusable, so
            # sanitize it the same way tmp dir names are sanitized in _mk_tmp (#8365).
            user = re.sub(r"[\\W]", "_", user)''')

by_task = {}
for task, path, old, new in E:
    s = open(path).read()
    n = s.count(old)
    if n != 1:
        print("  !! %s %s anchor matched %d times" % (task, os.path.basename(path), n))
        by_task.setdefault(task, []).append(False)
        continue
    open(path, "w").write(s.replace(old, new, 1))
    by_task.setdefault(task, []).append(True)

print("%-8s %-9s %-22s %s" % ("task", "edits", "diff", "checks"))
for task in sorted(by_task):
    repo = MAIN if task == "5227" else ROOT + "/wt/" + task
    ok = all(by_task[task]) and len(by_task[task]) == len([1 for t, *_ in E if t == task])
    f = os.path.join(repo, "src/_pytest")
    import py_compile, glob
    bad = []
    for py in glob.glob(f + "/**/*.py", recursive=True):
        try:
            py_compile.compile(py, doraise=True, cfile="/tmp/_x.pyc")
        except Exception as e:
            bad.append(os.path.basename(py))
    d = subprocess.run(["git", "-C", repo, "diff"], capture_output=True, text=True).stdout
    iid = {"5227": "pytest-dev__pytest-5227", "5413": "pytest-dev__pytest-5413",
           "5495": "pytest-dev__pytest-5495", "5692": "pytest-dev__pytest-5692",
           "6116": "pytest-dev__pytest-6116", "7220": "pytest-dev__pytest-7220",
           "7373": "pytest-dev__pytest-7373", "7432": "pytest-dev__pytest-7432",
           "8365": "pytest-dev__pytest-8365"}[task]
    open(ROOT + "/diffs/staged/%s.diff" % iid, "w").write(d)
    print("%-8s %-9s %-22s %s" % (task, "%d ok" % len(by_task[task]) if ok else "FAIL",
                                  iid + ".diff", "syntax clean" if not bad else "SYNTAX " + str(bad)))

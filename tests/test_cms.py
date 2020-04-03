###############################################################
# pytest -v --capture=no tests/1_local/test_name.py
# pytest -v  tests/1_local/test_name.py
# pytest -v --capture=no  tests/1_local/test_name..py::Test_name::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING

Benchmark.debug()

cloud = "local"


@pytest.mark.incremental
class TestName:

    def test_help(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_cms_admin(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms help admin", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert 'admin mongo status' in result

    def test_cms_check(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms help check", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert 'check [KEYWORDS...] [--output=OUTPUT]' in result

    def test_cms_source(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms help source", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert 'source list' in result

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)

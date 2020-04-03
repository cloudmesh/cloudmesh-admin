###############################################################
# pytest -v --capture=no tests/test_database.py
# pytest -v  tests/test_database.py
# pytest -v --capture=no  tests/test_database..py::Test_database::<METHODNAME>
###############################################################
# from cloudmesh.mongo import DatabaseUpdate
from pprint import pprint

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

Benchmark.debug()

database = CmDatabase()

user = Config()["cloudmesh.profile.user"]

name_generator = Name(
    schema=f"{user}-vm",
    counter=1)


#
# we need to set a cm = { kind, cloud, name } to use teh new DatabaseUpdate()
#


@pytest.mark.incremental
class TestMongo:

    def test_find_in_collection(self):
        HEADING()
        r = database.find_name("CC-CentOS7")
        pprint(r)

    def test_find_in_collections(self):
        HEADING()
        r = database.find_names("CC-CentOS7,CC-CentOS7-1811")
        pprint(r)

    def test_find_in_collection(self):
        HEADING()
        r = database.name_count("CC-CentOS7")
        pprint(r)

    def test_clear(self):
        HEADING()

        # print(self.name)
        # print(self.name.counter)
        # print(self.name.id(counter=100))

        database.clear()

        r = database.find()
        pprint(r)

        assert len(r) == 0

    def test_status(self):
        HEADING()
        r = database.status()
        # pprint(r)
        assert "Connection refused" not in r

        d = {}
        for field in ['uptime', 'pid', 'version', 'host']:
            d[field] = r[field]

        print(Printer.attribute(d))

        assert d is not None

    def test_update(self):
        HEADING()

        entries = [{"name": "Gregor"},
                   {"name": "Laszewski"}]

        for entry in entries:
            entry["cmid"] = str(self.name)
            entry["cmcounter"] = self.name.counter
            self.name.incr()
        database.update(entries)

        r = database.find()

        pprint(r)
        assert len(r) == 2

    def test_update2(self):
        HEADING()

        r = database.find(name="Gregor")
        pprint(r)

        assert r[0]['name'] == "Gregor"

    def test_update3(self):
        HEADING()
        entries = [{"cmcounter": 1, "name": "gregor"},
                   {"cmcounter": 2, "name": "laszewski"}]
        pprint(entries)
        for entry in entries:
            counter = entry["cmcounter"]
            print("Counter:", counter)
            entry["cmid"] = self.name.id(counter=counter)
        database.update(entries, replace=False)
        r = database.find()
        pprint(r)

    def test_update4(self):
        HEADING()
        r = database.find(name="gregor")
        pprint(r)
        assert r[0]["name"] == "gregor"

    def test_find_by_counter(self):
        HEADING()
        r = database.find_by_counter(1)
        pprint(r)
        assert r[0]["name"] == "gregor"

        r = database.find_by_counter(2)
        pprint(r)
        assert r[0]["name"] == "laszewski"

    def test_decorator_update(self):
        HEADING()

        @DatabaseUpdate()
        def entry():
            name = Name()
            print(name)
            d = {"cmid": str(name), "cmcounter": name.counter, "name": "albert"}
            name.incr()
            pprint(d)
            return d

        a = entry()

        r = database.find_by_counter(3)

        pprint(r)

    """
    def test_decorator_add(self):
        HEADING()

        @DatabaseAdd(collection="cloudmesh")
        def entry():
            d = {"name": "zweistein"}
            return d

        a = entry()

        r = database.find()

        pprint(r)

        assert len(r) == 4
    """

    def test_overwrite(self):
        HEADING()
        r = database.find(name="gregor")[0]
        pprint(r)
        r["color"] = "red"

        database.update([r], replace=True)

        r = database.find(color="red")

        pprint(r)

        assert len(r) == 1

    def test_fancy(self):
        HEADING()

        counter = 1

        n = Name(experiment="exp",
                 group="grp",
                 user="gregor",
                 kind="vm",
                 counter=counter)

        print(n)

        entries = [{
            "cmcounter": counter,
            "cmid": str(n),
            "name": "gregor",
            "phone": "android"
        }]
        database.update(entries, replace=True)

        r = database.find()

        pprint(r)

        assert len(r) == 4

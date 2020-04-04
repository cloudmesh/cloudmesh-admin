import json
import os
import textwrap
from pydoc import locate

from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


class ProviderCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/KeyCommand.py
    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/AkeyCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_provider(self, args, arguments):
        """
        ::

           Usage:
             provider list [--output=OUTPUT]
             provider info SERVICE NAME WHAT

           Arguments:
             NAME           The name of the key.

           Options:
              --output=OUTPUT               the format of the output [default: table]


           Description:

                What: output, sample

           Examples:
             Getting the sample and output from provides via a command

               cms provider info compute openstack sample
               cms provider info compute openstack output
               cms provider list --output=json
               cms provider list

        """

        def craete_list():
            _paths = []

            def find(names,
                     template="cloudmesh.compute.{name}",
                     kind=None,
                     on_error="not loaded"):
                _paths = []
                for _name in names:

                    _active = False
                    try:
                        _class = template.format(name=_name)
                        _p = locate(_class)
                        _where = _p.__file__
                        _path = os.path.dirname(_where)
                        _active = True
                        _provider = locate(f"{_class}.Provider.Provider")
                    except Exception as e:
                        _path = on_error.format(name=_name)
                        _provider = None
                    _paths.append({
                        "class": _class,
                        "path": _path,
                        "name": _name,
                        "active": _active,
                        "service": kind,
                        "provider": _provider
                    })
                return _paths

            # cloud_dir = os.path.dirname(locate("cloudmesh.compute").__file__)

            #
            # compute
            #
            candidates_compute_name = ["docker",
                                       "libcloud",
                                       "virtualbox",
                                       "vm"]

            candidates_name_compute = ["openstack",
                                       "azure",
                                       "google",
                                       "aws"
                                       "multipass"]

            _paths = find(candidates_compute_name,
                          template="cloudmesh.compute.{name}",
                          kind="compute",
                          on_error="load with pip install cloudmesh-cloud") + \
                     find(candidates_name_compute,
                          template="cloudmesh.{name}.compute",
                          kind="compute",
                          on_error="load with pip install cloudmesh-{name}")

            #
            # storage
            #
            candidates_storage_name = [
                "awss3",
                "azureblob",
                "box",
                "gdrive",
                "local",
                "parallelawss3",
                "parallelgdrive",
                "parallelazureblob"]

            candidates_name_storage = [
                "google",
                "oracle"]

            _paths += find(candidates_storage_name,
                           template="cloudmesh.storage.provider.{name}",
                           kind="storage",
                           on_error="load with pip install cloudmesh-storage") + \
                      find(candidates_name_storage,
                           template="cloudmesh.{name}.storage",
                           kind="storage",
                           on_error="load with pip install cloudmesh-{name}")

            candidates_volume = [
                "aws",
                "azure"
                "google",
                "multipass",
                "opensatck",
                "oracle"]

            _paths += find(candidates_volume,
                           template="cloudmesh.volume.provider.{name}",
                           kind="volume",
                           on_error="load with pip install cloudmesh-volume")
            return _paths

        map_parameters(arguments, 'output')

        if arguments.info:
            try:
                service = arguments.SERVICE
                name = arguments.NAME
                what = arguments.WHAT

                services = craete_list()

                for provider in services:

                    try:

                        if provider['service'] == service and \
                            provider['name'] == name:

                            if arguments.WHAT == 'sample':
                                print(textwrap.dedent(
                                    provider["provider"].sample))
                            elif arguments.WHAT == 'output':
                                print(json.dumps(provider["provider"].output,
                                                 indent=4))
                                print()


                    except Exception as e:
                        print(e)




            except:
                Console.error("Problem getting the Provider info")
                return ""

        elif arguments.list:

            print(arguments.output)
            _paths = craete_list()

            for entry in _paths:
                del entry["provider"]  # can not be printed
            print(
                Printer.write(_paths,
                              order=["service", "name", "active", "path"],
                              output=arguments.output)
            )

        return ""

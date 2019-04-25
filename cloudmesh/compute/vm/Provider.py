from cloudmesh.compute.libcloud.Provider import Provider as LibCloudProvider
from cloudmesh.compute.azure.AzProvider import Provider as AzAzureProvider
from cloudmesh.compute.docker.Provider import Provider as DockerProvider
from cloudmesh.compute.virtualbox.Provider import \
    Provider as VirtualboxCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.console import Console
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.parameter import Parameter
from multiprocessing import Pool

class Provider(ComputeNodeABC):

    def __init__(self, name=None,
                 configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        try:
            super().__init__(name, configuration)
            self.kind = Config(configuration)["cloudmesh"]["cloud"][name]["cm"][
                "kind"]
            self.credentials = Config(configuration)["cloudmesh"]["cloud"][name]["credentials"]

            self.name = name
        except:
            Console.error(f"provider {name} not found in {configuration}")
            raise ValueError(f"provider {name} not found in {configuration}")

        provider = None

        if self.kind in ["openstack", "aws", "google"]:
            provider = LibCloudProvider
        elif self.kind in ["vagrant", "virtualbox"]:
            provider = VirtualboxCloudProvider
        elif self.kind in ["docker"]:
            provider = DockerProvider
        elif self.kind in ["azure"]:
            provider = AzAzureProvider

        if provider is None:
            Console.error(f"provider {name} not supported")
            raise ValueError(f"provider {name} not supported")

        self.p = provider(name=name, configuration=configuration)

    def cloudname(self):
        return self.name

    def expand(self, names):
        if type(names) == list:
            return names
        else:
            return Parameter.expand(names)

    def loop(self, names, func, option='pool', processors=3):
        """
        :param option: if option is 'pool', use pool. if option is 'iter', use iteration
        """
        names = self.expand(names)
        r = []
        if option == 'pool':
            with Pool(processors) as p:
                r = p.map(func, names)
        elif option == 'iter':
            for name in names:
                vm = func(name)
                # vm.append(r)
                r.append(vm)
        else:
            print("looping option not supported")
        return r

    @DatabaseUpdate()
    def keys(self):
        return self.p.keys()

    @DatabaseUpdate()
    def list(self):
        return self.p.list()

    @DatabaseUpdate()
    def flavor(self):
        return self.p.flavors()

    def add_collection(self, d, *args):
        if d is None:
            return None
        label = '-'.join(args)
        for entry in d:
            entry['collection'] = label
        return d

    @DatabaseUpdate()
    def images(self):
        return self.p.images()

    # name
    # cloud
    # kind
    @DatabaseUpdate()
    def flavors(self):
        return self.p.flavors()

    @DatabaseUpdate()
    def start(self, names=None):
        return self.loop(names, self.p.start)

    @DatabaseUpdate()
    def stop(self, names=None):
        return self.loop(names, self.p.stop)

    def info(self, name=None):
        return self.p.info(name=name)

    @DatabaseUpdate()
    def resume(self, names=None):
        return self.loop(names, self.p.resume)

    @DatabaseUpdate()
    def reboot(self, names=None):
        return self.loop(names, self.p.reboot)

    @DatabaseUpdate()
    def create(self, names=None, image=None, size=None, timeout=360, **kwargs):
        names = self.expand(names)
        r = []
        for name in names:
            entry = self.p.create(
                        name=name,
                        image=image,
                        size=size,
                        timeout=360,
                        **kwargs)
            r.append(entry)
        return r

    def rename(self, source=None, destination=None):
        self.p.rename(source=source, destination=destination)

    def key_upload(self, key):
        self.p.key_upload(key)

    def destroy(self, names=None):
        return self.p.destroy(names=names)

    def ssh(self, names=None, command=None):
        names = self.expand(names)
        for name in names:
            return self.p.ssh(name=names,command=command)


    def login(self):
        if self.kind != "azure":
            raise NotImplementedError
        else:
            self.p.login()

    @DatabaseUpdate()
    def suspend(self, names=None):
        raise NotImplementedError

    @DatabaseUpdate()
    def destroy(self, names=None):
        raise NotImplementedError

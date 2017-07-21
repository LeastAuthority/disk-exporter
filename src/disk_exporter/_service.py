
from __future__ import unicode_literals

from functools import partial

from twisted.python.filepath import FilePath
from twisted.python.usage import Options
from twisted.internet.endpoints import serverFromString
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.application.service import MultiService
from twisted.application.internet import (
    TimerService,
    StreamServerEndpointService,
)

import attr

from nsenter import Namespace

from psutil import (
    disk_partitions,
    disk_usage,
)

from prometheus_client import Gauge
from prometheus_client.twisted import MetricsResource


class Options(Options):
    optParameters = [
        ("host-mount-namespace", None, None,
         "A path to a file representing the mount namespace which is to be monitored for disk stats.",
        ),
        ("metrics-port", None, b"tcp:9000",
         "A server endpoint description string on which to run a metrics-exposing server.",
        ),
    ]


_TOTAL = Gauge(
    "filesystem_size_bytes",
    "Total size in bytes of a filesystem",
    ["volume"],
)


_USED = Gauge(
    "filesystem_used_bytes",
    "Number of used bytes of a filesystem",
    ["volume"],
)


@attr.s(frozen=True)
class _DiskStats(object):
    name = attr.ib()

    def set(self, usage):
        _TOTAL.labels(volume=self.name).set(usage.total)
        _USED.labels(volume=self.name).set(usage.used)



class _DiskStatsCollector(object):
    def __init__(self):
        self._metrics = {}


    def _metric(self, mountpoint):
        try:
            metric = self._metrics[mountpoint]
        except KeyError:
            metric = _DiskStats(mountpoint)
            self._metrics[mountpoint] = metric
        return metric


    def _identifier(self, mountpoint):
        # AWS EBS volumes we particularly care about have a mountpoint like:
        # /var/lib/kubelet/pods/3e97440f-6356-11e7-844c-12050d0fa854/volumes/kubernetes.io~aws-ebs/pvc-8169664e-5b4a-11e7-95ba-12a44414a606
        if mountpoint.startswith("/var/lib/kubelet/pods/"):
            return FilePath(mountpoint).basename()
        return mountpoint


    def collect(self):
        for partition in disk_partitions():
            usage = disk_usage(partition.mountpoint)
            identifier = self._identifier(partition.mountpoint)
            metric = self._metric(identifier)
            metric.set(usage)



def collect_host_disk_stats(host_mount_namespace, collector):
    # Pop over into the host mount namespace.  Good thing we're not
    # multithreaded or this could really screw something up.
    with Namespace(host_mount_namespace, "mnt"):
        collector.collect()



def _get_collect_wrapper(namespace):
    if namespace is None:
        return lambda collector: collector.collect()
    else:
        return partial(collect_host_disk_stats, namespace)



def makeService(options):
    from twisted.internet import reactor

    parent = MultiService()

    root = Resource()
    root.putChild(b"metrics", MetricsResource())
    endpoint = serverFromString(reactor, options["metrics-port"])

    StreamServerEndpointService(
        endpoint,
        Site(root),
    ).setServiceParent(parent)


    TimerService(
        15,
        _get_collect_wrapper(
            options["host-mount-namespace"],
        ),
        _DiskStatsCollector(),
    ).setServiceParent(parent)


    return parent

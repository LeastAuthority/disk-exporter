
from twisted.application.service import ServiceMaker

disk_exporter = ServiceMaker(
    "Disk Stats Prometheus Exporter",
    "disk_exporter",
    "A daemon that reports disk stats in Prometheus format.",
    "disk-exporter",
)

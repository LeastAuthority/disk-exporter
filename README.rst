disk-exporter
=============

What is this?
-------------

``disk-exporter`` is a disk/filesystem stats collector.
It is aimed at enabling Prometheus-based monitoring of AWS EBS volumes in use on Kubernetes clusters.

It performs roughly the same task Prometheus's ``node-exporter`` performs but it deals with a containerized execution context better (it can find volumes visible to the host but not directly visible to the container).

How is it used?
---------------

Deploy it as a ``DaemonSet`` on your Kubernetes cluster.
It must be run a a privileged container with ``/proc/1/ns`` from the host mounted into it at ``/ns``.
It exposes Prometheus metrics on port 9000 at ``/metrics``.

License
-------

disk-exporter is open source software released under the MIT License.
See the LICENSE file for more details.

from setuptools import find_packages, setup

setup(
    name="disk-exporter",
    version="1.0",
    zip_safe=False,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    py_modules=["twisted.plugins.disk_exporter_dropin"],
    install_requires=[
        "twisted[tls]",
        "prometheus_client",
        "psutil",
        "nsenter",
        "attrs",
    ],
)

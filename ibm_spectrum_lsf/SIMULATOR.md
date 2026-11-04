# Trying IBM LSF Simulator

The simulator studies scheduling using cluster configurations and workload
traces. It does not execute our Monte Carlo worker and is not a replacement
for `LsfDispatcher`.

## Obtain the installer

IBM directs simulator downloads through
[Fix Central](https://www.ibm.com/support/fixcentral/). Select **IBM Spectrum
LSF Simulator**, then obtain the appropriate fix pack. IBM's
[release notes](https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=simulator-whats-new)
describe the available versions. Access and entitlement requirements depend on
the download; an installer has not been obtained for this codelab yet.

Installer names vary. IBM documents names such as
`lsf_cognitive_simulator_v1.tar.gz`; the extracted directory normally contains
the `bcogn` command. Use the instructions supplied with your exact package.

## Check the host

IBM's [installation guide](https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=simulator-installing)
lists Docker CE, x86-64 Linux, at least 32 GB RAM, 100 GB free installation
space, and free ports 2222, 5050, 9200, and 20022. It also requires
`vm.max_map_count` of at least 262144. OS and image support vary by fix pack.

```sh
docker info
free -h
df -h .
sysctl -n vm.max_map_count
ss -ltn
```

The host checked for this codelab has working Docker, free required ports,
about 20 GiB RAM, over 100 GB free disk, and `vm.max_map_count=1048576`.
**Its RAM is below IBM's documented requirement.** Nothing has been installed
or started, and no host settings have been changed.

## Start after obtaining the package

Inspect the included installation instructions and `License/` terms first.
IBM's installer assumes license acceptance before service startup. The package
starts multiple Docker services; it is not a single worker container.

Extract to a real absolute directory, avoiding symbolic links. From the
extracted directory, IBM documents these commands:

```sh
./bcogn -V
./bcogn start
./bcogn status
```

The web console is normally at `https://HOST:5050`. Use the package's own
certificate and authentication instructions. Ports and defaults may differ
between versions. To stop the service:

```sh
./bcogn stop
```

## First experiment

IBM's [simulator introduction](https://community.ibm.com/community/user/blogs/bill-mcmillan1/2020/03/13/to-be-or-not-to-be-well-it-depends)
describes bundled example workloads in its technical-preview package. If your
package includes examples, start with one of those; otherwise obtain a valid
LSF configuration and workload trace as required by the package documentation.

Run a baseline experiment, duplicate its configuration, change the available
host/core count, and repeat with the same workload. Compare job throughput,
pending time, and utilization. These are simulated scheduling results, not
Monte Carlo estimates. Do not rename our JSON task results to `lsb.events`;
they are different formats.

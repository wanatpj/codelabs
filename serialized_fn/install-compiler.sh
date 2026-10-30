#!/bin/bash
set -eu

. /etc/os-release
if [ "${VERSION_ID%%.*}" = 7 ]; then
    # UBI 7's public repos lack gcc-c++ and make; use the signed archive.
    cat > /etc/yum.repos.d/centos7-build.repo <<'EOF'
[centos7-build-base]
name=CentOS 7 build dependencies (archive)
baseurl=https://vault.centos.org/7.9.2009/os/$basearch/
enabled=1
gpgcheck=1
gpgkey=https://www.centos.org/keys/RPM-GPG-KEY-CentOS-7
EOF
fi

yum -y install gcc-c++ make
yum clean all

===========================
acu-ftp - command line tool
===========================

This program helps with checking and updating the ACU software over
ftp.  Downloading from the Flash is much faster than writing, so it is
usually efficient to pull the contents of the ACU, compare to what one
is trying to achieve, and write back only the differences.


Configuration file
==================

The config file is a yaml file.  By default the program looks for
acuftp.yaml in the current directory.

Example::

  # Patch descriptions
  patch_blocks:
    - name: config-test-config
      description: "
        SATP config from July 2021; includes a fix to allow up to 3
        control connections."
      steps:
        - bases/20210729
        - exempt: ["ntp.drift", "ntp.drift.TEMP"]
        - type: diff
          dir: pull_diffs/20220427_121335

  # Address to the ACU's FTP server, and base address of the storage.
  ftp_server:
    addr: "192.168.21.10"
    user: "xxx"
    pass: "yyy"
    root: "/ata0:1"

  storage:
    snapshots: "snapshots/"
    pull_diffs: "pull_diffs/"

ACU Simulator
=============

The scripts in the simulator/ directory can be used to simulate
communication with the ACU. This can be used to run the ACU Agent
without access to the ACU hardware.

The simulator responds to a basic subset of the ACU's HTTP API, enough
to be compatible with the SOCS ACU Agent's most important operations:

- ``go_to`` and ``set_boresight`` -- for simple moves
- ``generate_scan`` -- for constant elevation scanning
- ``monitor`` and ``broadcast`` processes -- for data stream
  production.


Run-time configuration
----------------------

Use environment varirables to alter the behavior of the simulator:

- ``ACUSIM_FLASK_LOG``: empty string or 0 will cause Flask logging to
  be suppressed.  Set to 1 for the usual flask logging of all
  requests
- ``ACUSIM_HTTP_PORT``: port on which to serve; defaults to 8102.
- ``ACUSIM_HTTP_BROADCAST_PORT``: port on which to broadcast UDP data
  frames; defaults to 10008.
- ``ACUSIM_PLATFORM``: Either 'ccat' or 'satp'.  Defaults to 'satp'.
  Note that simulation of LAT ('ccat') is currently a bit shallow --
  the main data set is renamed but not altered substantially.


Docker
------

To setup, first build the docker image::

    $ git clone https://github.com/simonsobs/soaculib.git
    $ cd soaculib/
    $ docker build -t soaculib .

Then you should be able to launch a simulator using the
``compose.yaml`` in the simulator directory::

    $ cd simulator/
    $ docker compose up

Alternately, start a simulator container like this::

    $ docker run -d --network="host" --rm soaculib python /app/soaculib/simulator/simulator_server.py


Clients
-------

In the soaculib default configuration blocks, the "simulator" block
matches the default configuration of the docker image, assuming it is
run on the same host as the soaculib client.

For example, to test the simulator in a Python session::

    >>> import soaculib
    >>> c = soaculib.AcuControl('simulator')
    >>> c.go_to(180, 60)
    'OK, Command executed.'

Here is a OCS site config file block::

    {'agent-class': 'ACUAgent',
     'instance-id': 'acu-emu',
     'arguments': [['--acu_config', 'simulator']]},


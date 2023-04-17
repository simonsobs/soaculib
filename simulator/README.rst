ACU Simulator
=============

The scripts here can be used to simulate communication with the
ACU. This can be used to run the ACU Agent without access to the ACU
hardware.

The simulator responds to a basic subset of the ACU's HTTP API, enough
to be compatible with the standard ACU Agent's most important
operations:

- ``go_to`` and ``set_boresight`` -- for simple moves
- ``generate_scan`` -- for constant elevation scanning
- ``monitor`` and ``broadcast`` processes -- for data stream
  production.


Docker
------

To setup, first build the docker image::

    $ git clone https://github.com/simonsobs/soaculib.git
    $ cd soaculib/
    $ docker build -t soaculib .

Then you should be able to launch a simulator using the
``docker-compose.yaml`` in the simulator directory::

    $ cd simulator/
    $ docker-compose up

Alternately, start a simulator container like this::

    $ docker run -d --network="host" --rm soaculib python /app/soaculib/simulator/simulator_server.py


Clients
-------

In the soaculib default configuration blocks, the "emulator" block
matches the default configuration of the docker image, assuming it is
run on the same host as the soaculib client.

For example, to test the emulator in a Python session::

    >>> import soaculib
    >>> c = soaculib.AcuControl('emulator')
    >>> c.go_to(180, 60)
    'OK, Command executed.'

Here is a OCS site config file block::

    {'agent-class': 'ACUAgent',
     'instance-id': 'acu-emu',
     'arguments': [['--acu_config', 'emulator']]},


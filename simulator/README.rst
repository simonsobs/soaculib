ACU Simulator
=============

The scripts here can be used to simulate communication with the ACU. This can
be used to run the ACU Agent without access to the ACU hardware.

To setup, first build the docker image::

    $ git clone https://github.com/simonsobs/soaculib.git
    $ cd soaculib/
    $ docker build -t soaculib .

Then you can startup the simulator container with::

    $ docker run -d --network="host" --rm soaculib python /app/soaculib/simulator/simulator_server.py

There is also a ``docker-compose.yaml`` provided to start the container::

    $ cd simulator/
    $ docker-compose up -d

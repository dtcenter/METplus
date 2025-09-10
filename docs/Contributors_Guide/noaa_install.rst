****************************************
Installation on the NOAA and MSU Systems
****************************************

The following instructions provide guidance for installing the METplus
components on the
`NOAA Research and Development High Performance Computing System (RDHPCS) <https://docs.rdhpcs.noaa.gov/index.html>`_.
and on the `MSU-HPC systems <https://www.hpc.msstate.edu/>`_.
The RDHPCS systems include Ursa, Hera, Jet, and Gaea. The MSU-HPC
systems include Orion and Hercules. These systems provide the computational
resources needed to run and evaluate the Model Evaluation Tools (MET)
and METplus framework. This documentation is intended for
METplus team members and collaborators who require a consistent and
reliable installation of the METplus components in the NOAA RDHPCS
environment. It outlines the necessary prerequisites, environment
configurations, and installation steps to ensure successful deployment
and use of METplus on these systems.


Log On
======

For these instructions, logging on to the RDHPCS systems is done using
the Secure Shell (SSH) protocol to one of the system’s bastions. RDHPCS
users with a CAC could alternatively use a CAC login.

Ursa, Hera, Jet, and Gaea Login
-------------------------------

The format for login is

.. code-block::

   ssh -Y <user-name>@<system-name>-rsa.<bastion>.rdhpcs.noaa.gov

where the :code:`<system-name>` and :code:`<bastion>` options are listed below.

.. role:: raw-html(raw)
    :format: html

.. list-table::

   * - RDHPCS System
     - RSA Bastion hostnames
   * - Ursa 
     - ursa-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` ursa-rsa.boulder.rdhpcs.noaa.gov
   * - Hera
     - hera-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` hera-rsa.boulder.rdhpcs.noaa.gov
   * - Jet
     - jet-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` jet-rsa.boulder.rdhpcs.noaa.gov
   * - Gaea
     - gaea-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` gaea-rsa.boulder.rdhpcs.noaa.gov

On **Ursa**, **Hera**, and **Jet** installations must be performed using the
:code:`role.metplus` account. After logging in with your personal account, switch to the role
account with the following command:

.. code-block::

   sudo su - role.metplus

This ensures that installations are done in the shared role environment rather than under an
individual user account.

.. note::

   On **Gaea**, the :code:`role.metplus` account is not available. In this case, you will
   perform the installation using your personal account.


Orion and Hercules Login
------------------------

The format for login is

.. code-block::

   ssh -Y <user-name>@<system-name>-dtn.hpc.msstate.edu

where the :code:`<system-name>` is either :code:`orion` or
:code:`hercules`.

While compilations may be done on any of the nodes, the development nodes serve the purpose
for software development and compiles in which additional system libraries may be requested
to be installed that are normally not required for runtime. Also, the development nodes
provide the only gateway for writing into the :code:`/apps/contrib/` directories.

The development nodes are:

.. role:: raw-html(raw)
    :format: html

.. list-table::

   * - MSU-HPC System
     - Development Nodes
   * - Orion
     - orion-devel-1 :raw-html:`<br />` orion-devel-2
   * - Hercules
     - hercules-devel-1 :raw-html:`<br />` hercules-devel-2

Switch to a development node with the following command:

.. code-block::

   ssh <development-node>

replacing :code:`<development-node>` with one of the development nodes from the table above.

On **Orion** and **Hercules**, installations must be performed using the
:code:`role-ovp` account. After logging in with your personal account, switch to the role
account with the following command:

.. code-block::

   sudo -su role-ovp

This ensures that installations are done in the shared role environment rather than under an
individual user account.





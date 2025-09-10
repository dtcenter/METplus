***************************************
Installation on the NOAA RDHPCS Systems
***************************************

The following instructions provide guidance for installing the METplus
components on the NOAA Research and Development High Performance
Computing System (RDHPCS). These systems provide the computational
resources needed to run and evaluate the Model Evaluation Tools (MET)
and METplus framework at scale. This documentation is intended for
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

Ursa, Hera, Jet, and Gaea Logins
--------------------------------

The format for login is
:code:`ssh -Y <user-name>@<system-name>-rsa.<bastion>.rdhpcs.noaa.gov`
where the :code:`<system-name>` and :code:`<bastion>` options are listed below.

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


       



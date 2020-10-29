Clone the Project Repository
----------------------------

Create a fresh working directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make a new directory to work in to ensure a fresh environment:

parsed-literal

.. raw:: html

   <details>
   <summary><a>Commands</a></summary>

.. parsed-literal::

    mkdir release-X.Y
    cd release-X.Y

.. raw:: html

   </details>

code-block

.. code-block::

    mkdir release-X.Y
    cd release-X.Y

Clone the project repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using SSH:

parsed-literal with replacement

.. parsed-literal::

    git clone git@github.com:dtcenter/|projectRepo|

parsed-literal without replacement

.. parsed-literal::

    git clone git@github.com:dtcenter/METplus


literal-block with replacement

::

    git clone git@github.com:dtcenter/|projectRepo|

literal-block without replacement

::

    git clone git@github.com:dtcenter/METplus

code-block

.. code-block::

    git clone git@github.com:dtcenter/|projectRepo|

Using HTTP:

.. parsed-literal::

    git clone https://github.com/dtcenter/|projectRepo|

Enter the project repository directory

.. parsed-literal::

    cd |projectRepo|

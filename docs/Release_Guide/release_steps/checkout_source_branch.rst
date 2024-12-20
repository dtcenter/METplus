Checkout the Source Branch
^^^^^^^^^^^^^^^^^^^^^^^^^^

Checkout the source branch based on the type of release to be created.

.. dropdown:: If creating a beta or rc1 release

  * If creating a **beta** (betaN) or **first release candidate** (rc1) release,
    checkout the develop branch:

  .. parsed-literal::

      git checkout develop

.. dropdown:: If creating an rc2+ release

  * If creating a **later release candidate** (rc2+) release,
    checkout the appropriate main branch:

  .. parsed-literal::

      git checkout main_vX.Y

Update the Documentation on the Web
-----------------------------------

- Regenerate the User's Guide and push the release to the gh-pages branch.
- For example, on kiowa:

.. parsed-literal::

    git clone https://github.com/dtcenter/MET
    cd MET/met/docs
    git checkout vX.Y.Z
    bash
    conda deactivate
    conda activate /home/met_test/.conda/envs/sphinx_env
    make html

- Store resulting html output files in the correct sub-directory on the gh-pages branch.

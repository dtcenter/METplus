# METplus Conda Recipe

This directory contains an internal copy of the conda recipe from the
[conda-forge metplus-feedstock](https://github.com/conda-forge/metplus-feedstock)
repository. It is used to test development releases (beta and rc) of METplus
and MET and to prepare recipe changes that will be ported to the feedstock
when an official release is available.

**IMPORTANT NOTE:** This recipe is only maintained on the **develop** branch.
Copies of these files on release branches (main_vX.Y) are not kept up to date
and should not be modified. The metplus-feedstock repository is the source of
truth for official releases, including bugfix releases, so changes for those
releases should be made directly in the feedstock.

## Updating the Recipe

When a new development release of METplus or MET is tagged, update
**recipe/meta.yaml**:

* Set **tag** and **met_tag** to the git tags without the leading "v",
  e.g. 13.0.0-rc1.
* Set **version** to the conda-compatible version of the METplus tag. Conda
  versions cannot contain hyphens, e.g. 13.0.0-rc1 becomes 13.0.0rc1.
* Update the **md5** and **sha256** hashes for both source tarballs:

```
curl -sSLf -o metplus.tar.gz https://github.com/dtcenter/METplus/archive/refs/tags/v<tag>.tar.gz
curl -sSLf -o met.tar.gz https://github.com/dtcenter/MET/archive/refs/tags/v<met_tag>.tar.gz
md5sum metplus.tar.gz met.tar.gz
sha256sum metplus.tar.gz met.tar.gz
```

On macOS, use **md5 -q** and **shasum -a 256** instead.

## Building Locally

Run the following from the top of the METplus repository:

```
conda build internal/scripts/conda/recipe -c conda-forge
```

**recipe/conda_build_config.yaml** sets the Python, compiler, and C standard
library versions used by local builds to match the pins used by the feedstock
CI. It is not used by the feedstock, which gets these values from
conda-forge-pinning.

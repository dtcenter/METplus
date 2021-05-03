# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -n
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Sphinx doesn't know to clean out the debris from sphinx-gallery
clean:
	rm -rf $(BUILDDIR)/* $(SOURCEDIR)/generated/met_tool_wrapper $(SOURCEDIR)/generated/model_applications

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# -w creates log file with warning messages
# create $(BUILDDIR) if it doesn't already exist so warnings log can be put in that directory
%: Makefile
	[ -d $(BUILDDIR) ] || mkdir -p $(BUILDDIR)
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -w "$(BUILDDIR)/warnings.log"

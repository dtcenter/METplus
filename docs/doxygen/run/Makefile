#
# Makefile for doc
#

##############
# Rules      #
##############

.PHONY: all
all: doc

.PHONY: clean doc clean_doc dist_clean_doc
doc:
	./clean && ./configure && ./compile
clean_doc:
	./clean
dist_clean_doc:
	./clean -a
clean: clean_doc

.PHONY: dist_clean
dist_clean: dist_clean_doc


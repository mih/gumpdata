BUILDDIR=$(CURDIR)/build
MAN_DIR=$(BUILDDIR)/man

PYTHON = python
PYTHON3 = python3
NOSETESTS = $(PYTHON) $(shell which nosetests)

# Setup local PYTHONPATH depending on the version of provided $(PYTHON)
PYVER = $(shell $(PYTHON) -c 'import sys; print(sys.version_info[0])')
ifeq ($(PYVER),2)
 # just use the local sources and run tests 'in source'
 TEST_DIR = .
 LPYTHONPATH = .:$(PYTHONPATH)
else
 # for 3 (and hopefully not above ;) ) -- corresponding build/
 # since sources go through 2to3 conversion
 TEST_DIR = $(BUILD3DIR)
 LPYTHONPATH = $(BUILD3DIR):$(PYTHONPATH)
endif

htmldoc:
	PYTHONPATH=..:$(LPYTHONPATH) sphinx-autogen \
			   -t doc/templates \
			   -o doc/source/generated doc/source/*.rst
	PYTHONPATH=..:$(LPYTHONPATH) $(MAKE) -C doc html BUILDDIR=$(BUILDDIR)

clean:
	rm -rf build
	rm -f MANIFEST
	rm -rf doc/source/generated

test:
	PYTHONPATH=$(LPYTHONPATH) $(NOSETESTS) \
		--nocapture \
		--exclude='external.*' \
		--with-doctest \
		--doctest-extension .rst \
		--doctest-tests doc/source/*.rst \
		.

release-%:
	@echo "Testing for uncommited changes"
	@git diff --quiet HEAD
	sed -i -e 's/^__version__ = .*$$/__version__ = "$(*)"/' gumpdata/__init__.py
	git add gumpdata/__init__.py
	@echo "Create and tag release commit"
	git commit -m "Release $(*)"
	git tag -s -a -m "Release $(*)" release/$(*)
	sed -i -e 's/^__version__ = .*$$/__version__ = "$(*)+dev"/' gumpdata/__init__.py
	git add gumpdata/__init__.py
	git commit -m "Increment version for new development cycle"



#
# Little helpers
#

mkdir-%:
	if [ ! -d $($*) ]; then mkdir -p $($*); fi

.PHONY: htmldoc clean manpages

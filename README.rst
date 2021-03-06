
This is a fork of ``emencia.recipe.patch``. Main differences are:

- Added Python 3 support.

Links:

- https://pypi.python.org/pypi/cykooz.recipe.patch - Download
- https://github.com/cykooz/cykooz.recipe.patch - Source code


Supported options
=================

The recipe supports the following options:

path
    Define a directory in which the patch should be applied. For
    example::

        path = src/some/directory/

egg
    Define which egg should be patched. You can also pin to a specific
    version. For example::

        egg = some.egg<=1.1.1

patches
    Paths to patch files. These patches are applied in order. For
    example::

        patches = patches/my_very_sprecial.patch
                  patches/another_loverly.patch

Example usage
=============

Our demo package which we will patch:

    >>> mkdir(sample_buildout, 'demo')
    >>> write(sample_buildout, 'demo', 'README.txt', " ")
    >>> write(sample_buildout, 'demo', 'demo.py',
    ... """# demo egg
    ... """)
    >>> write(sample_buildout, 'demo', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "demo",
    ...     version='1.0',
    ...     py_modules=['demo']
    ...     )
    ... """)
    >>> print_(system(buildout + ' setup demo bdist_egg')) # doctest: +ELLIPSIS
    Running setup script 'demo/setup.py'.
    ...

Create our patch:

    >>> write(sample_buildout, 'demo.patch',
    ... """diff --git demo.py demo.py
    ... --- demo.py
    ... +++ demo.py
    ... @@ -1 +1,2 @@
    ...  # demo egg
    ... +# patching
    ... """)

Let's write out buildout.cfg to patch our demo package:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = demo-patch
    ... index = demo/dist/
    ...
    ... [demo-patch]
    ... recipe = cykooz.recipe.patch
    ... egg = demo==1.0
    ... patches = demo.patch
    ... """)

Our final egg name depends on current python version:

    >>> import sys
    >>> demoegg = 'demo-1.0-py%d.%d.egg' % sys.version_info[:2]

Running the buildout gives us:

    >>> print_(system(buildout))
    Installing demo-patch.
    Getting distribution for 'demo==1.0'.
    Got demo 1.0.
    patch: reading patch .../demo.patch
    ...
    patch: patching file demo.py
    patch: successfully patched .../demo-1.0...
    ...

    >>> ls(sample_buildout, 'develop-eggs', demoegg)
    d  EGG-INFO
    -  demo.py
    -  demo.pyc
    -  demo.pyo
    >>> cat(sample_buildout, 'demo', 'demo.py')
    # demo egg
    >>> cat(sample_buildout, 'develop-eggs', demoegg, 'demo.py')
    # demo egg
    # patching

Multiple patches
----------------

If you have more than one patch to apply:

    >>> write(sample_buildout, 'another.patch',
    ... """diff --git demo.py demo.py
    ... --- demo.py
    ... +++ demo.py
    ... @@ -1,2 +1 @@
    ... -# demo egg
    ...  # patching
    ... """)

Update your buildout.cfg to list the new patch. In this case,
another.patch should be applied after demo.patch:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = demo-patch
    ... index = demo/dist/
    ...
    ... [demo-patch]
    ... recipe = cykooz.recipe.patch
    ... egg = demo==1.0
    ... patches =
    ...     demo.patch
    ...     another.patch
    ... """)

Running the buildout gives us:

    >>> rmdir(sample_buildout, 'develop-eggs', demoegg)
    >>> remove(sample_buildout, '.installed.cfg')
    >>> _ = system(buildout + ' setup demo bdist_egg')
    >>> print_(system(buildout))
    Installing demo-patch.
    Getting distribution for 'demo==1.0'.
    Got demo 1.0.
    patch: reading patch .../demo.patch
    ...
    patch: patching file demo.py
    patch: successfully patched .../demo-1.0...
    patch: reading patch .../another.patch
    ...
    patch: patching file demo.py
    patch: successfully patched .../demo-1.0...
    ...

    >>> cat(sample_buildout, 'develop-eggs', demoegg, 'demo.py')
    # patching

Patching an egg installed in another part
-----------------------------------------

Another possibility is to install an egg with zc.recipe.egg (or
probably any other recipe) and patch it afterwards.  However, it is
necessary to install the egg unzipped, and the egg may end up in the
eggs-folder instead the develop-eggs folder.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = demo-egg demo-patch
    ... index = demo/dist/
    ...
    ... [demo-egg]
    ... recipe = zc.recipe.egg
    ... eggs = demo==1.0
    ...
    ... [demo-patch]
    ... recipe = cykooz.recipe.patch
    ... egg = ${demo-egg:eggs}
    ... patches = demo.patch
    ... """)

Running the buildout gives us:

    >>> rmdir(sample_buildout, 'develop-eggs', demoegg)
    >>> remove(sample_buildout, '.installed.cfg')
    >>> _ = system(buildout + ' setup demo bdist_egg')
    >>> print_(system(buildout))
    Installing demo-egg.
    Getting distribution for 'demo==1.0'.
    Got demo 1.0.
    Installing demo-patch.
    patch: reading patch .../demo.patch
    ...
    patch: patching file demo.py
    patch: successfully patched .../demo-1.0...

    >>> ls(sample_buildout, 'eggs', demoegg)
    d  EGG-INFO
    -  demo.py
    -  demo.pyc
    -  demo.pyo
    >>> cat(sample_buildout, 'demo', 'demo.py')
    # demo egg
    >>> cat(sample_buildout, 'eggs', demoegg, 'demo.py')
    # demo egg
    # patching

Broken patches
--------------

If one of the patches is broken:

    >>> write(sample_buildout, 'missing-file.patch',
    ... """diff --git missing-file.py missing-file.py
    ... --- missing-file.py
    ... +++ missing-file.py
    ... @@ -1,2 +0 @@
    ... -# BROKEN
    ... -# PATCH
    ... """)

When you try to apply multiple patches, it will fail to apply any
subsequent patches, letting you fix the problem:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = demo-patch
    ... index = demo/dist/
    ...
    ... [demo-patch]
    ... recipe = cykooz.recipe.patch
    ... egg = demo==1.0
    ... patches = missing-file.patch
    ...           demo.patch
    ... """)

Running the buildout gives us:

    >>> rmdir(sample_buildout, 'eggs', demoegg)
    >>> remove(sample_buildout, '.installed.cfg')
    >>> _ = system(buildout + ' setup demo bdist_egg')
    >>> print_(system(buildout))
    Installing demo-patch.
    Getting distribution for 'demo==1.0'.
    Got demo 1.0.
    patch: reading patch .../missing-file.patch
    ...
    patch: The next patch would delete the file missing-file.py,
    patch: which does not exist!  Skipping patch.
    patch: patch: **** malformed patch at line 6:
    ...
    While:
      Installing demo-patch.
    Error: could not apply .../missing-file.patch

    >>> cat(sample_buildout, 'develop-eggs', demoegg, 'demo.py')
    # demo egg

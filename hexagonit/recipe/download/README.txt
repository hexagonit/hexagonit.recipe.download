Supported options
=================

The ``hexagonit.recipe.download`` recipe can be used to download and
extract packages from the net. It supports the following options:

``url``
    URL to the package that will be downloaded and extracted. The
    supported package formats are .tar.gz, .tar.bz2, and .zip. The
    value must be a full URL,
    e.g. http://python.org/ftp/python/2.4.4/Python-2.4.4.tgz.

``strip-top-level-dir``
    Switch to remove the top level directory from the
    extracted archive. This will work only if the archive has exactly
    one top level directory. Accepted values are 'true' or
    'false'. Defaults to 'false'.

``ignore-existing``
    Switch to ignore existing files and/or directories. By
    default, the extraction process fails if there is existing files
    or directories matching the ones from the archive. Enabling this
    option will skip these files/directories from the archive. When
    this recipe is uninstalled the ignored files/directories *will
    not* be removed. Accepted values are 'true' or 'false'. Defaults
    to 'false'.

``md5sum``
    MD5 checksum for the package file. If available the MD5
    checksum of the downloaded package will be compared to this value
    and if the values do not match the execution of the recipe will
    fail.

``destination``
    Path to a directory where the extracted contents of the package
    will be placed. If omitted, a directory will be created under the
    ``buildout['parts-directory']`` with the name of the section using
    the recipe.

``download-only``
    When set to 'true', the recipe downloads the file without trying
    to extract it. This is useful for downloading non-tarball
    files. The ``strip-top-level-dir`` option will be ignored if this
    option is enabled. Defaults to ``false``.

``filename``
    Allows renaming the downloaded file when using ``download-only = true``.
    The downloaded file will still be placed under the ``destination``
    directory with the given filename. If ``download-only = false`` this
    option will be ignored. By default the original filename will be used. New
    in version 1.4.1.

``hash-name``
    When set to 'true', passes the ``hash_name=True`` keyword parameter to the
    ``zc.buildout`` Download utility which in turn uses MD5 hashes to name the
    downloaded files. See the corresponding `documentation
    <http://pypi.python.org/pypi/zc.buildout#using-a-hash-of-the-url-as-the-filename-in-the-cache>`_
    for details. Setting the parameter to ``false`` will use the original
    filename. Defaults to ``true``. New in version 1.4.0.

The recipe uses the zc.buildout `Download API`_ to perform the
actual download which allows additional configuration of the download
process.

By default, the recipe sets the ``download-cache`` option to
``${buildout:directory}/downloads`` and creates the directory if
necessary. This can be overridden by providing the ``download-cache``
option in your ``[buildout]`` section.

.. _`Download API`: http://pypi.python.org/pypi/zc.buildout#using-the-download-utility


Simple example
==============

    >>> import os.path
    >>> testdata = join(os.path.dirname(__file__), 'testdata')
    >>> server = start_server(testdata)

In the simplest form we can download a simple package and have it
extracted in the parts directory.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %spackage1-1.2.3-final.tar.gz
    ... """ % server)

Ok, let's run the buildout:

    >>> print system(buildout)
    Installing package1.
    Downloading http://test.server/package1-1.2.3-final.tar.gz
    package1: Extracting package to /sample-buildout/parts/package1

Let's take a look at the buildout parts directory now.

    >>> ls(sample_buildout, 'parts')
    d package1

The containing directory is named after our part name. Within this
directory are the contents of the extracted package.

    >>> ls(sample_buildout, 'parts', 'package1')
    d package1-1.2.3-final

The package contained a single top level directory. Let's peek what's inside.

    >>> ls(sample_buildout, 'parts', 'package1', 'package1-1.2.3-final')
    - CHANGES.txt
    - README.txt
    d src

    >>> rmdir('downloads')

Sharing packages between buildouts
==================================

Using the ``download-cache`` option in the buildout allows you to
store the downloaded packages in central location on your
filesystem. Using the the same location for the ``download-cache`` in
multiple buildouts will effectively share the packages between them
and reduce the network traffic and storage requirements.

Let's create a directory to be used as the download cache.

    >>> cache = tmpdir('cache')

And create a new buildout that sets the ``buildout-cache`` option
accordingly.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = sharedpackage
    ... download-cache = %(cache)s
    ...
    ... [sharedpackage]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)spackage1-1.2.3-final.tar.gz
    ... """ % dict(cache=cache, server=server))

Ok, let's run the buildout:

    >>> print system(buildout)
    Uninstalling package1.
    Installing sharedpackage.
    Downloading http://test.server/package1-1.2.3-final.tar.gz
    sharedpackage: Extracting package to /sample-buildout/parts/sharedpackage

We can see that the package was placed under the shared container
instead of the default location under the buildout directory. By default the
the filename of the downloaded package is hashed.

    >>> ls(cache)
    -  dfb1e3136ba092f200be0f9c57cf62ec
    d  dist

We can keep the original filename by setting the ``hash-name`` parameter to
``false``. For readability all the following examples will have hashing
disabled.


MD5 checksums
=============

The downloaded package can be verified against an MD5 checksum. This will
make it easier to spot problems if the file has been changed.

If the checksum fails we get an error.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %spackage1-1.2.3-final.tar.gz
    ... md5sum = invalid
    ... hash-name = false
    ... """ % server)

    >>> print system(buildout)
    Uninstalling sharedpackage.
    Installing package1.
    Downloading http://test.server/package1-1.2.3-final.tar.gz
    While:
      Installing package1.
    Error: MD5 checksum mismatch downloading 'http://test.server/package1-1.2.3-final.tar.gz'

Using a valid checksum allows the recipe to proceed.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... hash-name = false
    ... """ % server)

    >>> print system(buildout)
    Installing package1.
    Downloading http://test.server//package1-1.2.3-final.tar.gz
    package1: Extracting package to /sample-buildout/parts/package1


Controlling the extraction process
==================================

We can also extract the archive to any arbitrary location and have the
top level directory be stripped, which is often a useful feature.

    >>> tmpcontainer = tmpdir('otherplace')
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... strip-top-level-dir = true
    ... hash-name = false
    ... """ % dict(server=server, dest=tmpcontainer))

Rerunning the buildout now gives us

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Extracting package to /otherplace

Taking a look at the extracted contents we can also see that the
top-level directory has been stripped.

    >>> ls(tmpcontainer)
    - CHANGES.txt
    - README.txt
    d src


Partial extraction over existing content
========================================

By default, the recipe will fail if the destination where the package
will be extracted already contains files or directories also included
in the package.

    >>> container = tmpdir('existing')
    >>> existingdir = mkdir(container, 'src')

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... strip-top-level-dir = true
    ... hash-name = false
    ... """ % dict(server=server, dest=container))

Running the buildout now will fail because of the existing ``src``
directory in the destination.

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Extracting package to /existing
    package1: Target /existing/src already exists. Either remove it or set ``ignore-existing = true`` in your buildout.cfg to ignore existing files and directories.
    While:
      Installing package1.
    Error: File or directory already exists.

Setting the ``ignore-existing`` option will allow the recipe to
proceed.

    >>> rmdir(container)
    >>> container = tmpdir('existing')
    >>> existingdir = mkdir(container, 'src')

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... strip-top-level-dir = true
    ... ignore-existing = true
    ... hash-name = false
    ... """ % dict(server=server, dest=container))

    >>> print system(buildout)
    Installing package1.
    package1: Extracting package to /existing
    package1: Ignoring existing target: /existing/src

    >>> ls(container)
    - CHANGES.txt
    - README.txt
    d src

Also note that when the recipe is uninstalled the ignored targets will
not be removed as they are not part of the output of this recipe. We
can verify this by running the buildout again with a different
destination.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... strip-top-level-dir = true
    ... ignore-existing = true
    ... hash-name = false
    ... """ % dict(server=server))

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Extracting package to /sample-buildout/parts/package1

Now when we look into the directory containing the previous buildout
we can see that the ``src`` directory is still there but the rest of
the files are gone.

    >>> ls(container)
    d src


Offline mode
============

If the buildout is run in offline mode the recipe will still work if
the package is cached in the downloads directory. Otherwise the user
will be informed that downloading the file is not possible in offline
mode.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ... offline = true
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... strip-top-level-dir = true
    ... hash-name = false
    ... """ % dict(server=server))

Let's verify that we do have a cached copy in our downloads directory.

    >>> ls(sample_buildout, 'downloads')
    -  package1-1.2.3-final.tar.gz

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Extracting package to /sample-buildout/parts/package1

When we remove the file from the filesystem the recipe will not work.

    >>> remove(sample_buildout, 'downloads', 'package1-1.2.3-final.tar.gz')
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package1
    ... offline = true
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)spackage1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... hash-name = false
    ... """ % dict(server=server))

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    While:
      Installing package1.
    Error: Couldn't download 'http://test.server/package1-1.2.3-final.tar.gz' in offline mode.


Downloading arbitrary files
===========================

We can download any file when setting the ``download-only`` option to
``true``. This will simply place the file in the ``destination``
directory.

    >>> empty_download_cache(cache)
    >>> downloads = tmpdir('my-downloads')
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package
    ... download-cache = %(cache)s
    ...
    ... [package]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)spackage1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... download-only = true
    ... """ % dict(server=server, dest=downloads, cache=cache))

    >>> print system(buildout)
    Installing package.
    Downloading http://test.server/package1-1.2.3-final.tar.gz

Looking into the destination directory we can see that the file was
downloaded but not extracted. Using the ``download-only`` option will
work for any file regardless of the type.

    >>> ls(downloads)
    -  package1-1.2.3-final.tar.gz

As seen above, with ``download-only`` the original filename will be preserved
regardless whether filename hashing is in use or not. However, the cached copy
will be hashed by default.

    >>> ls(cache)
    -  dfb1e3136ba092f200be0f9c57cf62ec
    d  dist

The downloaded files may also be renamed to better reflect their purpose using
the ``filename`` parameter.

    >>> empty_download_cache(cache)
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package
    ... download-cache = %(cache)s
    ...
    ... [package]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)spackage1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... download-only = true
    ... filename = renamed-package-1.2.3.tgz
    ... """ % dict(server=server, dest=downloads, cache=cache))

    >>> print system(buildout)
    Uninstalling package.
    Installing package.
    Downloading http://test.server/package1-1.2.3-final.tar.gz

    >>> ls(downloads)
    -  renamed-package-1.2.3.tgz

`Variable substitions
<http://pypi.python.org/pypi/zc.buildout#variable-substitutions>`_ may be used
with the ``filename`` parameter to generate the resulting filename dynamically.

    >>> empty_download_cache(cache)
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... newest = false
    ... parts = package
    ... download-cache = %(cache)s
    ... example = foobar-1.2.3
    ...
    ... [package]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)spackage1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... download-only = true
    ... filename = ${:_buildout_section_name_}-${buildout:example}.tgz
    ... """ % dict(server=server, dest=downloads, cache=cache))

    >>> print system(buildout)
    Uninstalling package.
    Installing package.
    Downloading http://test.server/package1-1.2.3-final.tar.gz

In this example we have used the section name and a value from the [buildout]
section to demonstrate the dynamic naming.

    >>> ls(downloads)
    -  package-foobar-1.2.3.tgz

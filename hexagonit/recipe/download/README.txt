Downloading and extracting packages
===================================

The ``hexagonit.recipe.download`` recipe can be used to download and
extract packages from the net. It supports the following options:

url
    URL to the package that will be downloaded and extracted. The
    supported package formats are .tar.gz, .tar.bz2, and .zip. The
    value must be a full URL,
    e.g. http://python.org/ftp/python/2.4.4/Python-2.4.4.tgz.

strip-top-level-dir
    Switch to remove the top level directory from the
    extracted archive. This will work only if the archive has exactly
    one top level directory. Accepted values are 'true' or
    'false'. Defaults to 'false'.

ignore-existing
    Switch to ignore existing files and/or directories. By
    default, the extraction process fails if there is existing files
    or directories matching the ones from the archive. Enabling this
    option will skip these files/directories from the archive. When
    this recipe is uninstalled the ignored files/directories *will
    not* be removed. Accepted values are 'true' or 'false'. Defaults
    to 'false'.

md5sum
    MD5 checksum for the package file. If available the MD5
    checksum of the downloaded package will be compared to this value
    and if the values do not match the execution of the recipe will
    fail.

destination
    The location where the extracted contents of the package
    will be placed. If omitted, a directory will be created under the
    ``buildout['parts-directory']`` with the name of the section using
    the recipe.

Additionally, the recipe honors the ``download-directory`` option set
in the ``[buildout]`` section and stores the downloaded files under
it. If the value is not set a directory called ``downloads`` will be
created in the root of the buildout and the ``download-directory``
option set accordingly.

The recipe will first check if there is a local copy of the package
before downloading it from the net. Files can be shared among
different buildouts by setting the ``download-directory`` to the same
location.

    >>> import os.path
    >>> testdata = join(os.path.dirname(__file__), 'testdata')
    >>> server = start_server(testdata)

In the simplest form we can download a simple package and have it
extracted in the parts directory.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %s/package1-1.2.3-final.tar.gz
    ... """ % server)

Ok, let's run the buildout:

    >>> print system(buildout)
    Installing package1.
    package1: Creating download directory: .../sample-buildout/downloads
    package1: Extracting package to .../sample-buildout/parts/package1

First of all, the recipe downloaded the package for us and placed it
in the downloads directory.

    >>> ls(sample_buildout, 'downloads')
    - package1-1.2.3-final.tar.gz

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

The downloaded package can be verified against a MD5 checksum. This will
make it easier to spot problems if the file has been changed.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... """ % server)

Ok, let's rerun the buildout.

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Using a cached copy from /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    package1: MD5 checksum OK
    package1: Extracting package to /sample-buildout/parts/package1

You will notice that the MD5 checksum was correct. Also rerunning the
buildout used the previously downloaded file from the ``downloads``
directory instead downloading it again from the net.

We can also extract the archive to any arbitrary location and have the
top level directory be stripped, which is often a useful feature.

    >>> tmpcontainer = tmpdir('otherplace')
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... strip-top-level-dir = true
    ... """ % dict(server=server, dest=tmpcontainer))

Rerunning the buildout now gives us

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Using a cached copy from /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    package1: MD5 checksum OK
    package1: Extracting package to /otherplace

Taking a look at the extracted contents we can also see that the
top-level directory has been stripped.

    >>> ls(tmpcontainer)
    - CHANGES.txt
    - README.txt
    d src

By default, the recipe will fail if the destination where the package
will be extracted already contains files or directories also included
in the package.

    >>> container = tmpdir('existing')
    >>> existingdir = mkdir(container, 'src')

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... strip-top-level-dir = true
    ... """ % dict(server=server, dest=container))

Running the buildout now will fail because of the existing ``src``
directory in the destination.

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Using a cached copy from /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    package1: MD5 checksum OK
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
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... destination = %(dest)s
    ... strip-top-level-dir = true
    ... ignore-existing = true
    ... """ % dict(server=server, dest=container))

    >>> print system(buildout)
    Installing package1.
    package1: Using a cached copy from /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    package1: MD5 checksum OK
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
    ... parts = package1
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... strip-top-level-dir = true
    ... ignore-existing = true
    ... """ % dict(server=server))

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Using a cached copy from /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    package1: MD5 checksum OK
    package1: Extracting package to /sample-buildout/parts/package1

Now when we look into the directory containing the previous buildout
we can see that the ``src`` directory is still there but the rest of
the files are gone.

    >>> ls(container)
    d src

If the buildout is run in offline mode the recipe will still work if
the package is cached in the downloads directory. Otherwise the user
will be informed that downloading the file is not possible in offline
mode.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package1
    ... offline = true
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... strip-top-level-dir = true
    ... """ % dict(server=server))

Let's verify that we do have a cached copy in our downloads directory.

    >>> ls(sample_buildout, 'downloads')
    - package1-1.2.3-final.tar.gz

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Using a cached copy from /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    package1: MD5 checksum OK
    package1: Extracting package to /sample-buildout/parts/package1

When we remove the file from the filesystem the recipe will not work.

    >>> remove(sample_buildout, 'downloads', 'package1-1.2.3-final.tar.gz')
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package1
    ... offline = true
    ...
    ... [package1]
    ... recipe = hexagonit.recipe.download
    ... url = %(server)s/package1-1.2.3-final.tar.gz
    ... md5sum = 821ecd681758d3fc03dcf76d3de00412
    ... """ % dict(server=server))

    >>> print system(buildout)
    Uninstalling package1.
    Installing package1.
    package1: Unable to download file in offline mode. Either run the buildout in online mode or place a copy of the file in /sample-buildout/downloads/package1-1.2.3-final.tar.gz
    While:
      Installing package1.
    Error: Download error

import os
import os.path
import urlparse
import urllib
import md5
import tempfile
import shutil
import setuptools.archive_util
import zc.buildout
import logging


class Recipe:
    """Recipe for downloading packages from the net and extracting them on
    the filesystem.
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        log = logging.getLogger(self.name)

        buildout['buildout'].setdefault(
            'download-directory',
            os.path.join(buildout['buildout']['directory'], 'downloads'))

        options.setdefault('destination', os.path.join(
                buildout['buildout']['parts-directory'],
                self.name))
        options.setdefault('strip-top-level-dir', 'false')
        options.setdefault('ignore-existing', 'false')
        options.setdefault('md5sum', '')

        try:
            _, _, urlpath, _, _, _ = urlparse.urlparse(options['url'])
            self.filename = urlpath.split('/')[-1]
        except IndexError:
            log.error('Unable to parse URL: %s' % options['url'])
            raise zc.buildout.UserError('Invalid URL')

    def update(self):
        pass

    def install(self):
        log = logging.getLogger(self.name)
        download_dir = self.buildout['buildout']['download-directory']
        destination = self.options.get('destination')


        if not os.path.isdir(download_dir):
            log.info('Creating download directory: %s' % download_dir)
            os.mkdir(download_dir)

        # Download the file if we don't have a local copy
        download_filename = os.path.join(download_dir, self.filename)
        if not os.path.exists(download_filename):
            if self.buildout['buildout']['offline'].lower() == 'true':
                log.error('Unable to download file in offline mode. Either '
                          'run the buildout in online mode or place a copy of '
                          'the file in %s' % download_filename)
                raise zc.buildout.UserError('Download error')
            urllib.urlretrieve(self.options['url'], download_filename)
        else:
            log.info('Using a cached copy from %s' % download_filename)

        # Verify file contents
        if self.options['md5sum'].strip():
            if compute_md5sum(download_filename) != self.options['md5sum'].strip():
                log.error('The file %s does not match the given MD5 checksum' % download_filename)
                raise zc.buildout.UserError('MD5 checksum error')
            log.info('MD5 checksum OK')

        # Extract the package
        extract_dir = tempfile.mkdtemp("buildout-" + self.name)
        try:
            setuptools.archive_util.unpack_archive(download_filename, extract_dir)
        except setuptools.archive_util.UnrecognizedFormat:
            log.error('Unable to extract the package %s. Unknown format.' % download_filename)
            raise zc.buildout.UserError('Package extraction error')

        # Move the contents of the package in to the correct destination
        top_level_contents = os.listdir(extract_dir)
        if self.options['strip-top-level-dir'].lower() in ('yes', 'true', '1', 'on'):
            if len(top_level_contents) != 1:
                log.error('Unable to strip top level directory because there are more '
                          'than one element in the root of the package.')
                raise zc.buildout.UserError('Invalid package contents')
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        parts = []

        if not os.path.isdir(destination):
            os.mkdir(destination)
            parts.append(destination)
        log.info('Extracting package to %s' % destination)

        ignore_existing = self.options['ignore-existing'].lower() in ('yes', 'true', '1', 'on')
        for filename in os.listdir(base):
            dest = os.path.join(destination, filename)
            if os.path.exists(dest):
                if ignore_existing:
                    log.info('Ignoring existing target: %s' % dest)
                else:
                    log.error('Target %s already exists. Either remove it or set '
                              '``ignore-existing = true`` in your buildout.cfg to ignore existing '
                              'files and directories.' % dest)
                    raise zc.buildout.UserError('File or directory already exists.')
            else:
                # Only add the file/directory to the list of installed
                # parts if it does not already exist. This way it does
                # not get accidentally removed when uninstalling.
                parts.append(dest)
            
            shutil.move(os.path.join(base, filename), dest)

        shutil.rmtree(extract_dir)
        return parts


def compute_md5sum(filename):
    hash = md5.new('')
    f = file(filename)
    chunk = f.read(2**16)
    while chunk:
        hash.update(chunk)
        chunk = f.read(2**16)
    return hash.hexdigest()

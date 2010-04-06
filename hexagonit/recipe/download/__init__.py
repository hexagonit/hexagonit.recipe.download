import logging
import os.path
import setuptools.archive_util
import shutil
import tempfile
import zc.buildout

from zc.buildout.download import Download

TRUE_VALUES = ('yes', 'true', '1', 'on')

class Recipe(object):
    """Recipe for downloading packages from the net and extracting them on
    the filesystem.
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        buildout['buildout'].setdefault(
            'download-cache',
            os.path.join(buildout['buildout']['directory'], 'downloads'))

        options.setdefault('destination', os.path.join(
                buildout['buildout']['parts-directory'],
                self.name))
        options['location'] = options['destination']
        options.setdefault('strip-top-level-dir', 'false')
        options.setdefault('ignore-existing', 'false')
        options.setdefault('download-only', 'false')
        options.setdefault('hash-name', 'true')

    def update(self):
        pass

    def calculate_base(self, extract_dir):
        """
        recipe authors inheriting from this recipe can override this method to set a different base directory.
        """
        log = logging.getLogger(self.name)
        # Move the contents of the package in to the correct destination
        top_level_contents = os.listdir(extract_dir)
        if self.options['strip-top-level-dir'].lower() in TRUE_VALUES:
            if len(top_level_contents) != 1:
                log.error('Unable to strip top level directory because there are more '
                          'than one element in the root of the package.')
                raise zc.buildout.UserError('Invalid package contents')
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir
        return base

    def install(self):
        log = logging.getLogger(self.name)

        if not os.path.exists(self.buildout['buildout']['download-cache']):
            os.makedirs(self.buildout['buildout']['download-cache'])

        destination = self.options.get('destination')
        download = Download(self.buildout['buildout'], hash_name=self.options['hash-name'].strip() in TRUE_VALUES)
        path, is_temp = download(self.options['url'], md5sum=self.options.get('md5sum'))

        parts = []

        try:
            # Create destination directory
            if not os.path.isdir(destination):
                os.makedirs(destination)
                parts.append(destination)

            download_only = self.options['download-only'].strip().lower() in TRUE_VALUES
            if download_only:
                # Simply copy the file to destination without extraction
                shutil.copy(path, destination)
                if not destination in parts:
                    parts.append(os.path.join(destination, os.path.basename(path)))
            else:
                # Extract the package
                extract_dir = tempfile.mkdtemp("buildout-" + self.name)
                try:
                    setuptools.archive_util.unpack_archive(path, extract_dir)
                except setuptools.archive_util.UnrecognizedFormat:
                    log.error('Unable to extract the package %s. Unknown format.', path)
                    raise zc.buildout.UserError('Package extraction error')

                base = self.calculate_base(extract_dir)

                if not os.path.isdir(destination):
                    os.makedirs(destination)
                    parts.append(destination)

                log.info('Extracting package to %s' % destination)

                ignore_existing = self.options['ignore-existing'].strip().lower() in TRUE_VALUES
                for filename in os.listdir(base):
                    dest = os.path.join(destination, filename)
                    if os.path.exists(dest):
                        if ignore_existing:
                            log.info('Ignoring existing target: %s' % dest)
                        else:
                            log.error('Target %s already exists. Either remove it or set '
                                      '``ignore-existing = true`` in your buildout.cfg to ignore existing '
                                      'files and directories.', dest)
                            raise zc.buildout.UserError('File or directory already exists.')
                    else:
                        # Only add the file/directory to the list of installed
                        # parts if it does not already exist. This way it does
                        # not get accidentally removed when uninstalling.
                        parts.append(dest)

                    shutil.move(os.path.join(base, filename), dest)

                shutil.rmtree(extract_dir)

        finally:
            if is_temp:
                os.unlink(path)

        return parts

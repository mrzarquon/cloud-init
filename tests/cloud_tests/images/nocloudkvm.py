# This file is part of cloud-init. See LICENSE file for license information.

"""NoCloud KVM Image Base Class."""

from cloudinit import util as c_util

from tests.cloud_tests.images import base
from tests.cloud_tests.snapshots import nocloudkvm as nocloud_kvm_snapshot


class NoCloudKVMImage(base.Image):
    """NoCloud KVM backed image."""

    platform_name = "nocloud-kvm"

    def __init__(self, platform, config, img_path):
        """Set up image.

        @param platform: platform object
        @param config: image configuration
        @param img_path: path to the image
        """
        self.modified = False
        self._img_path = img_path

        super(NoCloudKVMImage, self).__init__(platform, config)

    @property
    def properties(self):
        """Dictionary containing: 'arch', 'os', 'version', 'release'."""
        return {
            'arch': self.config['arch'],
            'os': self.config['family'],
            'release': self.config['release'],
            'version': self.config['version'],
        }

    def _execute(self, command, stdin=None, env=None):
        """Execute command in image, modifying image."""
        return self.mount_image_callback(command, stdin=stdin, env=env)

    def mount_image_callback(self, command, stdin=None, env=None):
        """Run mount-image-callback."""

        env_args = []
        if env:
            env_args = ['env'] + ["%s=%s" for k, v in env.items()]

        mic_chroot = ['sudo', 'mount-image-callback', '--system-mounts',
                      '--system-resolvconf', self._img_path,
                      '--', 'chroot', '_MOUNTPOINT_']
        try:
            out, err = c_util.subp(mic_chroot + env_args + list(command),
                                   data=stdin, decode=False)
            return (out, err, 0)
        except c_util.ProcessExecutionError as e:
            return (e.stdout, e.stderr, e.exit_code)

    def snapshot(self):
        """Create snapshot of image, block until done."""
        if not self._img_path:
            raise RuntimeError()

        instance = self.platform.create_image(
            self.properties, self.config, self.features,
            self._img_path, image_desc=str(self), use_desc='snapshot')

        return nocloud_kvm_snapshot.NoCloudKVMSnapshot(
            self.platform, self.properties, self.config,
            self.features, instance)

    def destroy(self):
        """Unset path to signal image is no longer used.

        The removal of the images and all other items is handled by the
        framework. In some cases we want to keep the images, so let the
        framework decide whether to keep or destroy everything.
        """
        self._img_path = None
        super(NoCloudKVMImage, self).destroy()

# vi: ts=4 expandtab

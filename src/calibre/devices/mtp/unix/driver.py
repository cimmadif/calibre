#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2012, Kovid Goyal <kovid at kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import operator
import pprint
import time
import traceback
from collections import namedtuple
from functools import partial
from threading import RLock

from calibre import as_unicode, force_unicode, prints
from calibre.constants import islinux, ismacos
from calibre.devices.errors import BlacklistedDevice, DeviceError, OpenActionNeeded, OpenFailed
from calibre.devices.mtp.base import MTPDeviceBase, debug, synchronous
from calibre.ptempfile import SpooledTemporaryFile

MTPDevice = namedtuple('MTPDevice', 'busnum devnum vendor_id product_id '
        'bcd serial manufacturer product')

null = object()


def fingerprint(d):
    return MTPDevice(d.busnum, d.devnum, d.vendor_id, d.product_id, d.bcd,
            d.serial, d.manufacturer, d.product)


def sorted_storage(storage_info):
    storage = sorted(storage_info, key=operator.itemgetter('id'))
    if len(storage) > 1 and storage[0].get('removable', False):
        for i in range(1, len(storage)):
            x = storage[i]
            if not x.get('removable', False):
                storage[0], storage[i] = storage[i], storage[0]
                break
    return storage


APPLE = 0x05ac


class MTP_DEVICE(MTPDeviceBase):

    supported_platforms = ['freebsd', 'linux', 'osx']

    def __init__(self, *args, **kwargs):
        MTPDeviceBase.__init__(self, *args, **kwargs)
        self.libmtp = None
        self.known_devices = None
        self.detect_cache = {}

        self.dev = None
        self._filesystem_cache = None
        self.lock = RLock()
        self.blacklisted_devices = set()
        self.ejected_devices = set()
        self.currently_connected_dev = None
        self._is_device_mtp = None
        if islinux:
            from calibre.devices.mtp.unix.sysfs import MTPDetect
            self._is_device_mtp = MTPDetect()
        if ismacos and 'osx' in self.supported_platforms:
            from calibre_extensions import usbobserver
            self.usbobserver = usbobserver
            self._is_device_mtp = self.osx_is_device_mtp

    def is_device_mtp(self, d, debug=None):
        ''' Returns True iff the _is_device_mtp check returns True and libmtp
        is able to probe the device successfully. '''
        if self._is_device_mtp is None:
            return False
        return (self._is_device_mtp(d, debug=debug) and
                self.libmtp.is_mtp_device(d.busnum, d.devnum))

    def osx_is_device_mtp(self, d, debug=None):
        if not d.serial:
            ans = False
        else:
            try:
                ans = self.usbobserver.is_mtp_device(d.vendor_id, d.product_id, d.bcd, d.serial)
            except Exception:
                if debug is not None:
                    import traceback
                    traceback.print_stack()
                return False
        if debug is not None and ans:
            debug(f'Device {d} claims to be an MTP device in the IOKit registry')
        return bool(ans)

    def set_debug_level(self, lvl):
        self.libmtp.set_debug_level(lvl)

    @synchronous
    def detect_managed_devices(self, devices_on_system, force_refresh=False):
        if self.libmtp is None:
            return None
        # First remove blacklisted devices.
        devs = set()
        for d in devices_on_system:
            fp = fingerprint(d)
            if fp not in self.blacklisted_devices and fp.vendor_id != APPLE:
                # Do not try to open Apple devices
                devs.add(fp)

        # Clean up ejected devices
        self.ejected_devices = devs.intersection(self.ejected_devices)

        # Check if the currently connected device is still present
        if self.currently_connected_dev is not None:
            return (self.currently_connected_dev if
                    self.currently_connected_dev in devs else None)

        # Remove ejected devices
        devs = devs - self.ejected_devices

        # Now check for MTP devices
        if force_refresh:
            self.detect_cache = {}
        cache = self.detect_cache
        for d in devs:
            ans = cache.get(d, None)
            if ans is None:
                ans = (
                    (d.vendor_id, d.product_id) in self.known_devices or
                    self.is_device_mtp(d))
                cache[d] = ans
            if ans:
                return d

        return None

    @synchronous
    def debug_managed_device_detection(self, devices_on_system, output):
        if self.currently_connected_dev is not None:
            return True
        p = partial(prints, file=output)
        if self.libmtp is None:
            err = 'startup() not called on this device driver'
            p(err)
            return False
        devs = [d for d in devices_on_system if
            ((d.vendor_id, d.product_id) in self.known_devices or
               self.is_device_mtp(d, debug=p)) and d.vendor_id != APPLE]
        if not devs:
            p('No MTP devices connected to system')
            return False
        p('MTP devices connected:')
        for d in devs:
            p(d)

        for d in devs:
            p('\nTrying to open:', d)
            try:
                self.open(d, 'debug')
            except BlacklistedDevice:
                p('This device has been blacklisted by the user')
                continue
            except Exception:
                p('Opening device failed:')
                p(traceback.format_exc())
                return False
            else:
                p('Opened', self.current_friendly_name, 'successfully')
                p('Storage info:')
                p(pprint.pformat(self.dev.storage_info))
                self.post_yank_cleanup()
                return True
        return False

    @synchronous
    def create_device(self, connected_device):
        d = connected_device
        man, prod = d.manufacturer, d.product
        man = force_unicode(man, 'utf-8') if isinstance(man, bytes) else man
        prod = force_unicode(prod, 'utf-8') if isinstance(prod, bytes) else prod
        return self.libmtp.Device(d.busnum, d.devnum, d.vendor_id,
                d.product_id, man, prod, d.serial)

    @synchronous
    def eject(self):
        if self.currently_connected_dev is None:
            return
        self.ejected_devices.add(self.currently_connected_dev)
        self.post_yank_cleanup()

    @synchronous
    def post_yank_cleanup(self):
        self.dev = self._filesystem_cache = self.current_friendly_name = None
        self.currently_connected_dev = None
        self.current_serial_num = None

    @property
    def is_mtp_device_connected(self):
        return self.currently_connected_dev is not None

    @synchronous
    def startup(self):
        try:
            from calibre_extensions import libmtp
        except Exception as err:
            print('Failed to load libmtp, MTP device detection disabled')
            print(err)
            self.libmtp = None
        else:
            self.libmtp = libmtp
            self.known_devices = frozenset(self.libmtp.known_devices())

            for x in vars(self.libmtp):
                if x.startswith('LIBMTP'):
                    setattr(self, x, getattr(self.libmtp, x))

    @synchronous
    def shutdown(self):
        self.dev = self._filesystem_cache = None

    def format_errorstack(self, errs):
        return '\n'.join(f'{code}:{as_unicode(msg)}' for code, msg in errs)

    @synchronous
    def open(self, connected_device, library_uuid):
        self.dev = self._filesystem_cache = None

        try:
            self.dev = self.create_device(connected_device)
        except Exception as e:
            self.blacklisted_devices.add(connected_device)
            raise OpenFailed(f'Failed to open {connected_device}: Error: {as_unicode(e)}')

        try:
            storage = sorted_storage(self.dev.storage_info)
        except self.libmtp.MTPError as e:
            if 'The device has no storage information.' in str(e):
                # This happens on newer Android devices while waiting for
                # the user to allow access. Apparently what happens is
                # that when the user clicks allow, the device disconnects
                # and re-connects as a new device.
                name = self.dev.friendly_name or ''
                if not name:
                    if connected_device.manufacturer:
                        name = connected_device.manufacturer
                    if connected_device.product:
                        name = name and (name + ' ')
                        name += connected_device.product
                    name = name or _('Unnamed device')
                raise OpenActionNeeded(name, _(
                    'The device {0} is not allowing connections.'
                    ' Unlock the screen on the {0}, tap "Allow" on any connection popup message you see,'
                    ' then either wait a minute or restart calibre. You might'
                    ' also have to change the mode of the USB connection on the {0}'
                    ' to "Media Transfer mode (MTP)" or similar.'
                ).format(name), (name, self.dev.serial_number))
            raise

        storage = [x for x in storage if x.get('rw', False)]
        if not storage:
            self.blacklisted_devices.add(connected_device)
            raise OpenFailed(f'No storage found for device {connected_device}')
        snum = self.dev.serial_number
        if snum in self.prefs.get('blacklist', []):
            self.blacklisted_devices.add(connected_device)
            self.dev = None
            raise BlacklistedDevice(
                f'The {connected_device} device has been blacklisted by the user')
        self._main_id = storage[0]['id']
        self._carda_id = self._cardb_id = None
        if len(storage) > 1:
            self._carda_id = storage[1]['id']
        if len(storage) > 2:
            self._cardb_id = storage[2]['id']
        self.current_friendly_name = self.dev.friendly_name
        if not self.current_friendly_name:
            self.current_friendly_name = self.dev.model_name or _('Unknown MTP device')
        self.current_serial_num = snum
        self.currently_connected_dev = connected_device

    @synchronous
    def device_debug_info(self):
        ans = self.get_gui_name()
        ans += f'\nSerial number: {self.current_serial_num}'
        ans += f'\nManufacturer: {self.dev.manufacturer_name}'
        ans += f'\nModel: {self.dev.model_name}'
        ans += f'\nids: {self.dev.ids}'
        ans += f'\nDevice version: {self.dev.device_version}'
        ans += '\nStorage:\n'
        storage = sorted_storage(self.dev.storage_info)
        ans += pprint.pformat(storage)
        return ans

    def _filesystem_callback(self, fs_map, entry, level):
        name = entry.get('name', '')
        self.filesystem_callback(_('Found object: %s')%name)
        fs_map[entry.get('id', null)] = entry
        path = [name]
        pid = entry.get('parent_id', 0)
        while pid != 0 and pid in fs_map:
            parent = fs_map[pid]
            path.append(parent.get('name', ''))
            pid = parent.get('parent_id', 0)
            if fs_map.get(pid, None) is parent:
                break  # An object is its own parent
        path = tuple(reversed(path))
        ok = not self.is_folder_ignored(self._currently_getting_sid, path)
        if not ok:
            debug('Ignored object: {}'.format('/'.join(path)))
        return ok

    @property
    def filesystem_cache(self):
        if self._filesystem_cache is None:
            st = time.time()
            debug('Loading filesystem metadata...')
            from calibre.devices.mtp.filesystem_cache import FilesystemCache
            with self.lock:
                storage, all_items, all_errs = [], [], []
                for sid, capacity in zip([self._main_id, self._carda_id,
                    self._cardb_id], self.total_space()):
                    if sid is None:
                        continue
                    name = _('Unknown')
                    for x in self.dev.storage_info:
                        if x['id'] == sid:
                            name = x['name']
                            break
                    storage.append({'id':sid, 'size':capacity,
                        'is_folder':True, 'name':name, 'can_delete':False,
                        'is_system':True})
                    self._currently_getting_sid = str(sid)
                    items, errs = self.dev.get_filesystem(sid,
                            partial(self._filesystem_callback, {}))
                    all_items.extend(items), all_errs.extend(errs)
                if not all_items and all_errs:
                    raise DeviceError(
                            f'Failed to read filesystem from {self.current_friendly_name} with errors: {self.format_errorstack(all_errs)}')
                if all_errs:
                    prints('There were some errors while getting the '
                            f' filesystem from {self.current_friendly_name}: {self.format_errorstack(all_errs)}')
                self._filesystem_cache = FilesystemCache(storage, all_items)
            debug(f'Filesystem metadata loaded in {time.time()-st:g} seconds ({len(self._filesystem_cache)} objects)')
        return self._filesystem_cache

    @synchronous
    def get_basic_device_information(self):
        d = self.dev
        return (self.current_friendly_name, d.device_version, d.device_version, '')

    @synchronous
    def total_space(self, end_session=True):
        ans = [0, 0, 0]
        for s in self.dev.storage_info:
            i = {self._main_id:0, self._carda_id:1,
                    self._cardb_id:2}.get(s['id'], None)
            if i is not None:
                ans[i] = s['capacity']
        return tuple(ans)

    @synchronous
    def free_space(self, end_session=True):
        self.dev.update_storage_info()
        ans = [0, 0, 0]
        for s in self.dev.storage_info:
            i = {self._main_id:0, self._carda_id:1,
                    self._cardb_id:2}.get(s['id'], None)
            if i is not None:
                ans[i] = s['freespace_bytes']
        return tuple(ans)

    @synchronous
    def create_folder(self, parent, name):
        if not parent.is_folder:
            raise ValueError(f'{parent.full_path} is not a folder')
        e = parent.folder_named(name)
        if e is not None:
            return e
        sid, pid = parent.storage_id, parent.object_id
        if pid == sid:
            pid = 0
        ans, errs = self.dev.create_folder(sid, pid, name)
        if ans is None:
            raise DeviceError(
                    f'Failed to create folder named {name} in {parent.full_path} with error: {self.format_errorstack(errs)}')
        return parent.add_child(ans)

    @synchronous
    def put_file(self, parent, name, stream, size, callback=None, replace=True):
        e = parent.folder_named(name)
        if e is not None:
            raise ValueError(f'Cannot upload file, {parent.full_path} already has a folder named: {e.name}')
        e = parent.file_named(name)
        if e is not None:
            if not replace:
                raise ValueError(f'Cannot upload file {e.full_path}, it already exists')
            self.delete_file_or_folder(e)
        sid, pid = parent.storage_id, parent.object_id
        if pid == sid:
            pid = 0xFFFFFFFF

        ans, errs = self.dev.put_file(sid, pid, name, stream, size, callback)
        if ans is None:
            raise DeviceError(f'Failed to upload file named: {name} to {parent.full_path}: {self.format_errorstack(errs)}')
        return parent.add_child(ans)

    @synchronous
    def get_mtp_file(self, f, stream=None, callback=None):
        if f.is_folder:
            raise ValueError(f'{f.full_path} if a folder')
        set_name = stream is None
        if stream is None:
            stream = SpooledTemporaryFile(5*1024*1024, '_wpd_receive_file.dat')
        ok, errs = self.dev.get_file(f.object_id, stream, callback)
        if not ok:
            raise DeviceError(f'Failed to get file: {f.full_path} with errors: {self.format_errorstack(errs)}')
        stream.seek(0)
        if set_name:
            stream.name = f.name
        return stream

    @synchronous
    def list_mtp_folder_by_name(self, parent, *names: str):
        if not parent.is_folder:
            raise ValueError(f'{parent.full_path} is not a folder')
        parent_id = self.libmtp.LIBMTP_FILES_AND_FOLDERS_ROOT if parent.is_storage else parent.object_id
        x = self.dev.list_folder_by_name(parent.storage_id, parent_id, names)
        if x is None:
            raise FileNotFoundError(f'Could not find folder named: {"/".join(names)} in {parent.full_path}')
        return x

    @synchronous
    def get_mtp_metadata_by_name(self, parent, *names: str):
        if not parent.is_folder:
            raise ValueError(f'{parent.full_path} is not a folder')
        parent_id = self.libmtp.LIBMTP_FILES_AND_FOLDERS_ROOT if parent.is_storage else parent.object_id
        x = self.dev.get_metadata_by_name(parent.storage_id, parent_id, names)
        if x is None:
            raise DeviceError(f'Could not find file named: {"/".join(names)} in {parent.full_path}')
        m, errs = x
        if not m:
            raise DeviceError(f'Failed to get metadata for: {"/".join(names)} in {parent.full_path} with errors: {self.format_errorstack(errs)}')
        return m

    @synchronous
    def get_mtp_file_by_name(self, parent, *names: str, stream=None, callback=None):
        if not parent.is_folder:
            raise ValueError(f'{parent.full_path} is not a folder')
        set_name = stream is None
        if stream is None:
            stream = SpooledTemporaryFile(5*1024*1024, '_wpd_receive_file.dat')
        parent_id = self.libmtp.LIBMTP_FILES_AND_FOLDERS_ROOT if parent.is_storage else parent.object_id
        x = self.dev.get_file_by_name(parent.storage_id, parent_id, names, stream, callback)
        if x is None:
            raise FileNotFoundError(f'Could not find file named: {"/".join(names)} in {parent.full_path}')
        ok, errs = x
        if not ok:
            raise DeviceError(f'Failed to get file: {"/".join(names)} in {parent.full_path} with errors: {self.format_errorstack(errs)}')
        stream.seek(0)
        if set_name:
            stream.name = '/'.join(names)
        return stream

    @synchronous
    def delete_file_or_folder(self, obj):
        if obj.deleted:
            return
        if not obj.can_delete:
            raise ValueError(f'Cannot delete {obj.full_path} as deletion not allowed')
        if obj.is_system:
            raise ValueError(f'Cannot delete {obj.full_path} as it is a system object')
        if obj.files or obj.folders:
            raise ValueError(f'Cannot delete {obj.full_path} as it is not empty')
        parent = obj.parent
        ok, errs = self.dev.delete_object(obj.object_id)
        if not ok:
            raise DeviceError(f'Failed to delete {obj.full_path} with error: {self.format_errorstack(errs)}')
        parent.remove_child(obj)
        return parent

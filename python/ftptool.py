import argparse
import ftplib
import os
import subprocess as sp
import tempfile
import time
import yaml


class ftpHelper:
    def __init__(self, cfg):
        self.F = ftplib.FTP(cfg['addr'])
        self.F.login(cfg['user'], cfg['pass'])

    def mkdir(self, dir_name):
        """Create directory described by dir_name.  This will create any
        missing components of the tree.

        """
        comps = dir_name.split('/')[1:]
        i = len(comps)
        while i > 0:
            test = '/' + '/'.join(comps[:i])
            try:
                self.F.cwd(test)
                break
            except Exception:
                pass
            i -= 1
        while i < len(comps):
            test = '/' + '/'.join(comps[:i+1])
            self.F.mkd(test)
            i += 1

    def put(self, src, dest, verbose=False):
        """Take file at src and copy it to dest.  If dest ends in '/', it's
        interpreted as a directory and src's basename is used.

        """
        basename = os.path.split(src)[1]
        if dest.endswith('/'):
            dest = dest + basename
        size = os.path.getsize(src)
        # Book-keep the transfer
        timer = {
            't0': time.time(),
            't1':  time.time(),
            'n0': 0,
            'n1': 0}

        def update_sent(blob):
            global t0, t1, n0, n1
            timer['n0'] += len(blob)
            timer['n1'] += len(blob)
            now = time.time()
            if now - timer['t1'] > 5:
                n0, n1 = timer['n0'], timer['n1']
                rate0 = n0 / (now - timer['t0'])
                rate1 = n1 / (now - timer['t1'])
                print(' ... %i of %i [%.1f%%] rate=%.1fkB/s avg_rate=%.1fkB/s' %
                      (n0, size, (n0/size)*100, rate1/1e3, rate0/1e3))
                timer['t1'], timer['n1'] = now, 0
        callback = update_sent if verbose else None
        self.F.storbinary(f'STOR {dest}', open(src, 'rb'),
                          callback=callback)

    def rmdir(self, dir_name):
        self.F.rmd(dir_name)

    def rm(self, f):
        print(f)
        self.F.delete(f)

    def pull_file(self, src, dest):
        """Pull file at src and store it in dest.  If dest ends with a /, then
        the basename of the source file is added.  Otherwise, it's
        treated as the destination filename.

        """
        p, f = os.path.split(src)
        if dest.endswith('/'):
            dest = dest + f
        dest_dir = os.path.split(dest)[0]
        if dest_dir != '' and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with open(dest, 'wb') as fout:
            self.F.retrbinary('RETR %s' % src, fout.write)

    def scan_tree(self, root, recurse=True, prefix='', exclude='$'):
        """Crawl through all files and directories on the server starting
        from directory ``root``.

        Returns:
          dirs: list of all directories.
          files: list of all files.

        Each dir and file is given relative to root (without a leading
        /).

        """
        assert(root.startswith('/'))
        lines = []
        self.F.dir(root, lambda x: lines.append(x))
        dirs, files = [], []
        for line in lines:
            w = line.split(None, 8)
            perms, fn = w[0], w[-1]
            if perms[0] == 'd':
                if len(exclude) and fn[0] in exclude:
                    continue
                dirs.append(fn)
            else:
                files.append(os.path.join(prefix, fn))
        new_dirs = [os.path.join(prefix, d) for d in dirs]
        if recurse:
            for d in dirs:
                _d, _f = self.scan_tree(
                    root + '/' + d, True, os.path.join(prefix, d))
                files.extend(_f)
                new_dirs.extend(_d)
        return new_dirs, files

    def pull_listing(self, root, dest_dir, dirs, files):
        """Given the list of dirs and files, copy them to dest_dir starting
        from root.

        """
        for _d in dirs:
            _d = dest_dir + '/' + _d
            if not os.path.exists(_d):
                os.makedirs(_d)
        for _f in files:
            self.pull_file(os.path.join(root, _f), os.path.join(dest_dir, _f))

    def checksum_listing(self, root, files):
        """Checksum all files from the remote.

        Returns a list, the same length as files, with the
        corresponding md5sums.

        """
        checksums = []
        with tempfile.TemporaryDirectory() as tempd:
            filename = os.path.join(tempd, 'file')
            for _f in files:
                self.pull_file(root + '/' + _f, filename)
                checksums.append(get_md5(filename))
        return checksums

    def rm_listing(self, root, dirs, files):
        for _f in files:
            self.rm(root + '/' + _f)
        for _d in sorted(dirs)[::-1]:
            self.rmdir(root + '/' + _d)


class RemoteScan:
    def __init__(self, cache_file, max_age=0, refresh=None, ftp_cfg=None):
        self.cache_file = cache_file
        if refresh is True:
            return self.refresh(ftp_cfg)
        if os.path.exists(cache_file):
            age = time.time() - os.path.getmtime(cache_file)
            if age > max_age and refresh is not False:
                self.refresh(ftp_cfg)
            else:
                self._read()
        else:
            self.refresh(ftp_cfg)

    def _read(self):
        print('Reading from %s' % self.cache_file)
        pairs = [x.strip().split(' ', 1) for x in open(self.cache_file)]
        self.files = {b: (b, a) for a, b in pairs}

    def refresh(self, ftp_cfg):
        f = ftpHelper(ftp_cfg)
        root = ftp_cfg['root']
        print(f'Snapshot based at {root}...')
        print(' ... scanning')
        ds, fs = f.scan_tree(root)
        print(' ... checksumming')
        t0 = time.time()
        checksums = f.checksum_listing(root, fs)
        lines = (sorted([[d, 'dir'] for d in ds]) +
                 sorted(list(zip(fs, checksums))))
        print(' ... writing to %s' % self.cache_file)
        with open(self.cache_file, 'w') as fout:
            for a, b in lines:
                fout.write('%s %s\n' % (b, a))
        print(' ... finished in %.1f seconds' % (time.time() - t0))
        self._read()


class Patch:
    def __init__(self, config=[]):
        self.files = {}
        for c in config:
            self._add_patch(c)

    def _add_patch(self, patch):
        if isinstance(patch, str):
            patch = {'dir': patch}
        if 'type' not in patch:
            if 'dir' in patch:
                patch['type'] = 'dir'
            if 'exempt' in patch:
                patch['type'] = 'exempt'

        if patch['type'] == 'dir':
            base = patch['dir']
            self._add_patch_dir(base)

        elif patch['type'] == 'diff':
            base = patch['dir']
            self._add_patch_dir(os.path.join(base, 'data'))
            to_remove = yaml.safe_load(open(os.path.join(base, 'remove.yaml')))
            for f in to_remove.keys():
                try:
                    self.files.pop(f)
                except KeyError:
                    pass

        elif patch['type'] == 'exempt':
            for f in patch['exempt']:
                self.files[f] = ['', 'exempt']

    def _add_patch_dir(self, base):
        if not os.path.exists(base):
            raise RuntimeError(f"Patch refered to data_dir={base}, which "
                               " does not exist.")
        for root, dirs, files in os.walk(base):
            for path_list, checksum in [(dirs, 'dir'),
                                        (files, None)]:
                for f in path_list:
                    full_path = os.path.join(root, f)
                    dest_path = full_path[len(base)+1:]
                    self.files[dest_path] = [full_path, checksum]

    def checksum(self):
        for k, v in self.files.items():
            if v[1] is None:
                v[1] = get_md5(v[0])


def get_md5(filename):
    p = sp.Popen(['md5sum', filename], stdout=sp.PIPE)
    out, _ = p.communicate()
    return out.decode('utf8').split()[0]


def fs_and_ds(both, keys_only=False):
    fs = {k: v for k, v in both.items() if v != 'dir'}
    ds = {k: v for k, v in both.items() if v == 'dir'}
    if keys_only:
        fs, ds = list(fs.keys()), list(ds.keys())
    return fs, ds


def ftpatch(patcher, remote_root, to_copy, to_remove,
            clean=False, verbose=False):
    """Patch the tree over ftp, by copying in new things and removing some
    unwanted things.

    Args:
      patcher: object to perform operations (an FTPHelper or a Dummy).
      remote_root: base path on the FTP server
      to_copy: dict with files to copy and dirs to create on server
      to_remove: list of files and dirs to remove from server
      clean (bool): actually perform the removal?

    """
    # Create missing dirs.
    for remote_path, (source, check) in to_copy.items():
        if check == 'dir':
            remote_full = os.path.join(remote_root, remote_path)
            print(f'mkdir {remote_full}')
            patcher.mkdir(remote_full)
    # Create / update files.
    for remote_path, (source, check) in to_copy.items():
        if check != 'dir':
            remote_full = os.path.join(remote_root, remote_path)
            print(f'upload {remote_full}')
            patcher.put(source, remote_full,
                        verbose=verbose)
    # Remove stuff?
    if clean:
        to_remove = sorted([(check == 'dir', os.path.join(remote_root, remote_path))
                            for remote_path, check in to_remove])
        for is_dir, remote_full in to_remove:
            if is_dir:
                print(f'rmdir {remote_full}')
                patcher.rmdir(os.path.join(remote_full))
            else:
                print(f'rm {remote_full}')
                patcher.rm(os.path.join(remote_full))

class Dummy:
    def mkdir(self, d):
        print(f' MKDIR {d}')
    def put(self, src, dest, verbose=False):
        print(f' PUT {dest} <- {src}')
    def rmdir(self, d):
        print(f' RMDIR {d}')
    def rm(self, f):
        print(f' RM {f}')


def timecode(t=None):
    FORMAT = '%Y%m%d_%H%M%S'
    if t is None:
        t = time.time()
    return time.strftime(FORMAT, time.gmtime(t))

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', '-c', default=None)
    parser.add_argument('--verbose', '-v', action='store_true')
    s = parser.add_subparsers(dest='action')

    p = s.add_parser('prompt', help="Connect to FTP but then do nothing.  If "
                     "you ran python with -i you can access the ftp object.")

    p = s.add_parser('snapshot', help="Download contents from FTP source "
                     "and store in a dated directory, with a user message.")
    p.add_argument('message')
    p.add_argument('-o', '--output')

    p = s.add_parser('patch', help="Compare what is on the FTP remote with "
                     "a set of local files defined in the config file.")
    p.add_argument('--list', action='store_true', help=
                   "Take no action other than to list the named patch blocks.")
    p.add_argument('--apply', action='store_true', help=
                   "Send new/updated files to the FTP destination.")
    p.add_argument('--clean', action='store_true', help=
                   "... and also remove unwanted files.")
    p.add_argument('--pull-diff', action='store_true', help=
                   "Instead of applying the local file set, download "
                   "all the files on the FTP remote that differ.")
    p.add_argument('--name', help="Choose a specific patch defined "
                   "in the config file (integer index works too).")

    p = s.add_parser('checksum', help="Checksum a single file from the FTP remote.")
    p.add_argument('path_on_server')

    p = s.add_parser('get-file', help="Download a file from FTP remote.")
    p.add_argument('path_on_server', help="Filename on FTP server.")
    p.add_argument('local_dest', nargs='?', default=None, help="Local dest dir (end in /) "
                   "or filename; defaults to ./.")

    p = s.add_parser('put-file', help="Upload a file to the FTP remote.")
    p.add_argument('local_source', help="Local path to file.")
    p.add_argument('path_on_server', help="Filename or dir on server.  If dir, end with /.")
    p.add_argument('-f', '--force', action='store_true')

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    # Load config ...
    if args.config_file is None:
        # Load from env?
        args.config_file = os.getenv('ACUFTP_CONFIG', None)
        if args.config_file is None:
            args.config_file = 'acuftp.yaml'
    config = yaml.safe_load(open(args.config_file).read())

    # Update ftp cfg...
    ftp_cfg = config['ftp_server']

    if args.action == 'snapshot':
        if args.output is None:
            args.output = os.path.join(config['storage']['snapshots'],
                                       timecode())
        data_dir = os.path.join(args.output, 'data')
        os.makedirs(data_dir, exist_ok=True)
        print('Snapshot will be written to %s' % args.output)
        with open(os.path.join(args.output, 'info.txt'), 'w') as f:
            f.write('User message:\n')
            f.write(args.message + '\n')
        print()

        ftp = ftpHelper(ftp_cfg)
        root = ftp_cfg['root']
        print(f'Snapshot based at {root}...')
        print(' ... scanning')
        ds, fs = ftp.scan_tree(root)
        t0 = time.time()
        print(' ... downloading')
        t0 = time.time()
        ftp.pull_listing(root, data_dir, ds, fs)
        print(' ... finished in %.1f seconds' % (time.time() - t0))

    elif args.action == 'patch':
        patch_blocks = config['patch_blocks']
        if args.list:
            print(f'There are {len(patch_blocks)} named patch blocks:')
            for i, patch_block in enumerate(patch_blocks):
                print('   %2i.  %s' % (i, patch_block['name']))
            print()
            parser.exit()

        patch_index = None
        try:
            patch_index = int(args.name)
        except ValueError:
            pass

        if args.name is None:
            print('Using the first patch block from config file ...')
            patch_block = patch_blocks[0]
        else:
            for i, patch_block in enumerate(patch_blocks):
                if patch_block['name'] == args.name:
                    break
                if i == patch_index:
                    break
            else:
                parser.error('No patch block called "%s"' % args.name)

        print('Reading in patch block "%s"' % patch_block['name'])
        patch = Patch(patch_block['steps'])
        patch.checksum()

        remote = RemoteScan('remote_checksums.txt', max_age=6000, ftp_cfg=ftp_cfg)

        local_only = {k: v for k, v in patch.files.items()
                      if v[1] not in ['exempt', 'ignore']}
        remote_only = {}
        mismatch = {}
        ok = {}
        for filename, remote_check in remote.files.values():
            if filename in patch.files:
                local_file, local_check = patch.files[filename]
                if remote_check != local_check and local_check != 'exempt':
                    mismatch[filename] = [local_file, local_check]
                else:
                    ok[filename] = [filename, local_check]
                try:
                    local_only.pop(filename)
                except KeyError:
                    pass
            else:
                remote_only[filename] = [filename, remote_check]

        is_clean = True
        for heading, listing in [
                ('Found in local patch only:', local_only),
                ('Found on remote ftp only:', remote_only),
                ('Mismatching data:', mismatch),
        ]:
            if len(listing):
                is_clean = False
                print(heading)
                for item in listing.keys():
                    print('  ', item)
                print()

        if is_clean:
            print()
            print('The FTP remote matches the local file definition exactly.')
            print()
            parser.exit()

        # Check for onlies on local / remote that differ only in case.
        # This isn't a perfect solution but will get us through.
        case_conflicts = {k.lower(): [k] for k in local_only.keys()}
        for k in remote_only.keys():
            if k.lower() in case_conflicts:
                case_conflicts[k.lower()].append(k)
        case_conflicts = {k: v for k, v in case_conflicts.items() if len(v) > 1}
        if len(case_conflicts):
            print('Warning! Local and remote refer to filenames that differ '
                  'only in case:')
            for n1, n2 in case_conflicts.values():
                print('  %s  -->  %s' % (n1, n2))
            print()
            print('The files on the left *will* be copied to the remote, but '
                  'the files on the right *will not* be cleaned from the remote '
                  '(even if --clean is passed).')
            print()

        # So ... what things to copy, what things to remove?
        to_copy = {}
        remove = []
        for k in local_only:
            to_copy[k] = local_only[k]
        for k in mismatch:
            to_copy[k] = mismatch[k]
        for k in remote_only:
            if not k.lower() in case_conflicts:
                remove.append((k, remote_only[k][1]))

        if args.apply:
            ftp = ftpHelper(ftp_cfg)
            ftpatch(ftp, ftp_cfg['root'], to_copy, remove,
                    clean=args.clean)
        elif args.pull_diff:
            ftp = ftpHelper(ftp_cfg)
            print(config['storage'])
            out_dir = os.path.join(config['storage']['pull_diffs'],
                                   timecode())
            os.makedirs(out_dir + '/data', exist_ok=True)
            fs1, ds1 = fs_and_ds(remote_only, True)
            fs2, ds2 = fs_and_ds(mismatch, True)
            print('Saving pull-diff to %s' % out_dir)
            print(' ... downloading')
            t0 = time.time()
            ftp.pull_listing(ftp_cfg['root'],
                             out_dir + '/data', ds1+ds2, fs1+fs2)
            print(' ... finished in %.1f seconds' % (time.time() - t0))
            with open(os.path.join(out_dir, 'remove.yaml'), 'w') as fout:
                fout.write(yaml.dump(local_only))
        else:
            print('Pass --apply to upload the changes (and --clean too maybe)')

    elif args.action == 'prompt':
        f = ftpHelper(ftp_cfg)
        print('f is your ftpHelper')

    elif args.action == 'get-file':
        if args.local_dest is None:
            args.local_dest = './'
        f = ftpHelper(ftp_cfg)
        f.pull_file(args.path_on_server, args.local_dest)

    elif args.action == 'put-file':
        if args.path_on_server[-1] == '/':
            args.path_on_server = os.path.join(args.path_on_server,
                                               os.path.split(args.local_source)[1])
        elif not args.force:
            raise RuntimeError('Pass --force if you are writing to a '
                               'different filename on remote.')
        f = ftpHelper(ftp_cfg)
        f.put(args.local_source, args.path_on_server)

    elif args.action == 'checksum':
        f = ftpHelper(ftp_cfg)
        with tempfile.TemporaryDirectory() as tempd:
            fn = os.path.join(tempd, 'local')
            f.pull_file(args.path_on_server, fn)
            checksum = get_md5(fn)
        print(checksum)

    else:
        parser.print_help()

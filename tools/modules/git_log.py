# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Simple module for inspecting git commits

import os
import subprocess


class GitCommit:
    __slots__ = (
        "sha1",
        # to extract more info
        "_git_dir",

        # cached values
        "_author",
        "_date",
        "_body",
        "_files",
        "_files_status",
    )

    def __init__(self, sha1, git_dir):
        self.sha1 = sha1
        self._git_dir = git_dir

        self._author = \
            self._date = \
            self._body = \
            self._files = \
            self._files_status = \
            None

    def cache(self):
        """ Cache all properties
        """
        self.author
        self.date
        self.body
        self.files
        self.files_status

    def _log_format(self, format, args=()):
        # sha1 = self.sha1.decode('ascii')
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "log",
            "-1",  # only this rev
            self.sha1,
            "--format=" + format,
        ) + args
        # print(" ".join(cmd))

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        )
        return p.stdout.read()

    @property
    def sha1_short(self):
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "rev-parse",
            "--short",
            self.sha1,
        )
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        )
        return p.stdout.read().strip().decode('ascii')

    @property
    def author(self):
        ret = self._author
        if ret is None:
            content = self._log_format("%an")[:-1]
            ret = content.decode("utf8", errors="ignore")
            self._author = ret
        return ret

    @property
    def date(self):
        ret = self._date
        if ret is None:
            import datetime
            ret = datetime.datetime.fromtimestamp(int(self._log_format("%ct")))
            self._date = ret
        return ret

    @property
    def body(self):
        ret = self._body
        if ret is None:
            content = self._log_format("%B")[:-1]
            ret = content.decode("utf8", errors="ignore")
            self._body = ret
        return ret

    @property
    def subject(self):
        return self.body.lstrip().partition("\n")[0]

    @property
    def files(self):
        ret = self._files
        if ret is None:
            ret = [f for f in self._log_format("format:", args=("--name-only",)).split(b"\n") if f]
            self._files = ret
        return ret

    @property
    def files_status(self):
        ret = self._files_status
        if ret is None:
            ret = [f.split(None, 1) for f in self._log_format("format:", args=("--name-status",)).split(b"\n") if f]
            self._files_status = ret
        return ret

    def show(self, args=()):
        """
        Output of git-show.
        """
        cmd = (
            "git",
            # "-c", "color.diff=always",
            "--git-dir",
            self._git_dir,
            "show",
            self.sha1,
        ) + args
        # print(" ".join(cmd))

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        )
        return p.stdout.read()



class GitCommitIter:
    __slots__ = (
        "_path",
        "_git_dir",
        "_git_extra_args",
        "_sha1_range",
        "_process",
    )

    def __init__(self, path, sha1_range, extra_args=()):
        self._path = path
        self._git_dir = os.path.join(path, ".git")
        self._sha1_range = sha1_range
        self._process = None
        self._git_extra_args = extra_args

    def __iter__(self):
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "log",
            self._sha1_range,
            "--format=%H",
            *self._git_extra_args,
        )
        # print(" ".join(cmd))

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        )
        return self

    def __next__(self):
        sha1 = self._process.stdout.readline()[:-1]
        if sha1:
            return GitCommit(sha1, self._git_dir)
        else:
            raise StopIteration


class GitRepo:
    __slots__ = (
        "_path",
        "_git_dir",
    )

    def __init__(self, path):
        self._path = path
        self._git_dir = os.path.join(path, ".git")

    @property
    def branch(self):
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        )
        # print(" ".join(cmd))

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        )
        return p.stdout.read()

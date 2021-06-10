# Copyright 2020 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import tests.utils as utils

import jujucrashdump.crashdump as crashdump


class TestCrashCollector(utils.BaseTestCase):
    def setUp(self):
        self.target = crashdump.CrashCollector("aModel", 42, ["extra_dir"])
        self._patches = {}
        self._patches_start = {}

    def tearDown(self):
        self.target = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def patch_target(self, attr, return_value=None):
        mocked = mock.patch.object(self.target, attr)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def test_create_unit_tarballs(self):
        self.patch_object(crashdump, "DIRECTORIES")
        self.target.uniq = "fake-uuid"
        self.patch_target("_run_all")
        self.DIRECTORIES.__iter__.return_value = ["dir"]
        self.target.create_unit_tarballs()
        self._run_all.assert_called_with(
            "tar --append -f /tmp/fake-uuid/juju-dump-fake-uuid.tar "
            "-C /tmp/fake-uuid/cmd_output . || true;"
            "tar --append -f /tmp/fake-uuid/juju-dump-fake-uuid.tar "
            "-C /tmp/fake-uuid/ journalctl || true;"
            "tar --append -f /tmp/fake-uuid/juju-dump-fake-uuid.tar "
            "-C /tmp/fake-uuid/addon_output . || true"
        )
        self._run_all.reset_mock()
        self.target.exclude = ("exc0", "exc1")
        self.target.create_unit_tarballs()
        self._run_all.assert_called_with(
            "tar --append -f /tmp/fake-uuid/juju-dump-fake-uuid.tar "
            "-C /tmp/fake-uuid/cmd_output . || true;"
            "tar --append -f /tmp/fake-uuid/juju-dump-fake-uuid.tar "
            "-C /tmp/fake-uuid/ journalctl || true;"
            "tar --append -f /tmp/fake-uuid/juju-dump-fake-uuid.tar "
            "-C /tmp/fake-uuid/addon_output . || true"
        )

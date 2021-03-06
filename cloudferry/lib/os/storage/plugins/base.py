# Copyright 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc


class VolumeObjectNotFoundError(RuntimeError):
    pass


class CinderMigrationPlugin(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_volume_object(self, context, volume_id):
        """:returns" `FileObject` which corresponds to cinder volume object
        based on :arg volume_id:
        :raises: VolumeObjectNotFoundError if volume object does not exist"""
        raise NotImplementedError()

    def cleanup(self, context, volume_id):
        pass

    @classmethod
    @abc.abstractmethod
    def from_context(cls, context):
        """Builds cinder plugin from context provided"""
        raise NotImplementedError()

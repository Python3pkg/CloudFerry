# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and#
# limitations under the License.

"""
Module to update migration scenario file migrate.yaml, during execution,
point to insert fail step ('fail_migration') is being chosen randomly by
_insert_break_point method from list of steps generated by _get_list_of_tasks
method.
"""

import os
import random
import yaml

import utils


class RollbackScenarioGeneration(object):
    def __init__(self):
        self.utils = utils.Utils()
        self.file_path = 'devlab/tests/scenarios/cold_migrate.yaml'
        self.full_path = os.path.join(self.utils.main_folder, self.file_path)
        self.exception_task = {'fail_migration': True}
        self.steps_list = []

    def _read_migrationation_file(self):
        return self.utils.load_file(self.file_path)[0]

    @staticmethod
    def _dump_into_file(file_path, data):
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    @staticmethod
    def _verification(_step):
        if isinstance(_step, dict):
            if isinstance(_step.values()[0], bool) or \
                    isinstance(_step.values()[0], list) and \
                    len(_step.values()[0]) == 1:
                return True

    def _get_list_of_tasks(self, search_dict):
        for key, value in search_dict.iteritems():
            if self._verification(search_dict):
                self.steps_list.append(search_dict)
            elif isinstance(value, list):
                for item in value:
                    self._get_list_of_tasks(item)
            elif isinstance(value, dict):
                self._get_list_of_tasks(value)
        return self.steps_list

    def _insert_break_point(self, search_dict, field):
        for key, value in search_dict.iteritems():
            if isinstance(value, dict):
                if self._verification(value):
                    return
                else:
                    self._insert_break_point(value, field)
            elif isinstance(value, list):
                if field in value:
                    index = value.index(field) + 1
                    value.insert(index, self.exception_task)
                    return
                else:
                    for item in value:
                        if isinstance(item, dict):
                            self._insert_break_point(item, field)

    def _find_break_point(self, search_dict, field):
        fields_found = []
        for key, value in search_dict.iteritems():
            if key == field:
                fields_found.append(value)
            elif isinstance(value, dict):
                results = self._find_break_point(value, field)
                for result in results:
                    fields_found.append(result)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self._find_break_point(item, field)
                        for another_result in more_results:
                            fields_found.append(another_result)
        return fields_found

    def generate_exception_task_in_random_point(self):
        migration_data = self._read_migrationation_file()
        data = None
        for key, value in migration_data.iteritems():
            if key == 'process':
                data = {key: value}
        list_of_steps = self._get_list_of_tasks(data)
        random_step = random.choice(list_of_steps)
        self._insert_break_point(data, random_step)
        print('\n\nBreak point was set after:\n{}, index: {}\n\n'.format(
            random_step, list_of_steps.index(random_step)))
        try:
            assert(self._find_break_point(migration_data,
                                          self.exception_task.keys()[0])
                   == self.exception_task.values())
            self._dump_into_file(self.full_path, migration_data)
        except Exception as e:
            print('Integration of failure step into migration scenario failed '
                  'with following error: \n\n{}'.format(e))

if __name__ == '__main__':
    rollback = RollbackScenarioGeneration()
    rollback.generate_exception_task_in_random_point()

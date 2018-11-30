#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file contains the code to load test the golang recommendation service.

Copyright © 2018 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
from locust import HttpLocust, TaskSet, task
from collections import Counter

stats = {"host-distribution": Counter()}


class StackAnalysisUserBehaviour(TaskSet):
    """This class defines the user behaviours."""

    def on_start(self):
        """on_start is called when a Locust start before any task is scheduled."""
        pass

    @task
    def trigger_stack_analysis_five_package_stack(self):
        """Simulate a stack analysis request."""
        stack = ["github.com/ugorji/go/codec", "github.com/golang/glog", "a"]
        response = self.client.post("/api/v1/companion_recommendation",
                                    data=json.dumps({"package_list": stack,
                                                     "comp_package_count_threshold": 5}),
                                    headers={'Content-type': 'application/json'})
        print(response)


class StackAnalysisUserLocust(HttpLocust):
    """This class defines the params for the load testing piece."""

    task_set = StackAnalysisUserBehaviour
    min_wait = 10
    max_wait = 10

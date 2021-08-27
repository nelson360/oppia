# coding: utf-8
#
# Copyright 2021 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers responsible for managing Apache Beam jobs."""

from __future__ import absolute_import
from __future__ import unicode_literals

from core.controllers import acl_decorators
from core.controllers import base
from core.domain import beam_job_services
import feconf
from jobs import jobs_manager

from typing import Any, Dict # isort: skip


class BeamJobHandler(base.BaseHandler):
    """Handler for getting the definitions of Apache Beam jobs."""

    GET_HANDLER_ERROR_RETURN_TYPE = feconf.HANDLER_TYPE_JSON
    URL_PATH_ARGS_SCHEMAS: Dict[str, Any] = {}
    HANDLER_ARGS_SCHEMAS: Dict[str, Any] = {
        'GET': {}
    }

    @acl_decorators.can_run_any_job
    def get(self) -> None:
        self.render_json({
            'jobs': [j.to_dict() for j in beam_job_services.get_beam_jobs()]
        })


class BeamJobRunHandler(base.BaseHandler):
    """Handler for managing the execution of Apache Beam jobs."""

    GET_HANDLER_ERROR_RETURN_TYPE = feconf.HANDLER_TYPE_JSON
    URL_PATH_ARGS_SCHEMAS: Dict[str, Any] = {}
    HANDLER_ARGS_SCHEMAS: Dict[str, Any] = {
        'GET': {},
        'PUT': {
            'job_name': {
                'schema': {
                    'type': 'unicode'
                }
            },
            'job_arguments': {
                'schema': {
                    'type': 'list',
                    'items': {
                        'type': 'unicode'
                    },
                }
            },
        },
    }

    @acl_decorators.can_run_any_job
    def get(self) -> None:
        sorted_beam_job_runs = sorted(
            beam_job_services.get_beam_job_runs(),
            key=lambda j: j.job_updated_on,
            reverse=True)

        self.render_json({
            'runs': [r.to_dict() for r in sorted_beam_job_runs]
        })

    @acl_decorators.can_run_any_job
    def put(self) -> None:
        job_name = (
            self.normalized_payload.get('job_name')
            if self.normalized_payload else None)
        job_arguments = (
            self.normalized_payload.get('job_arguments')
            if self.normalized_payload else None)

        beam_job_run = jobs_manager.run_job_sync(job_name, job_arguments)
        self.render_json(beam_job_run.to_dict())


class BeamJobRunResultHandler(base.BaseHandler):
    """Handler for getting the result of Apache Beam jobs."""

    GET_HANDLER_ERROR_RETURN_TYPE = feconf.HANDLER_TYPE_JSON
    URL_PATH_ARGS_SCHEMAS: Dict[str, Any] = {}
    HANDLER_ARGS_SCHEMAS: Dict[str, Any] = {
        'GET': {
            'job_id': {
                'schema': {
                    'type': 'basestring'
                }
            }
        }
    }

    @acl_decorators.can_run_any_job
    def get(self) -> None:
        job_id = self.request.get('job_id')
        result = beam_job_services.get_beam_job_run_result(job_id)
        self.render_json(result.to_dict())
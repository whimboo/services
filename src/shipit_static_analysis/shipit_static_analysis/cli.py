# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from shipit_static_analysis.workflow import Workflow
from shipit_static_analysis import config
from cli_common.click import taskcluster_options
from cli_common.log import init_logger
from cli_common.taskcluster import get_secrets
import click
import logging
import re

logger = logging.getLogger(__name__)

REGEX_COMMIT = re.compile(r'(\w+):(\d+):(\d+)')


@click.command()
@taskcluster_options
@click.argument('commits', envvar='COMMITS')
@click.option(
    '--cache-root',
    required=True,
    help='Cache root, used to pull changesets'
)
def main(commits,
         cache_root,
         taskcluster_secret,
         taskcluster_client_id,
         taskcluster_access_token,
         ):

    secrets = get_secrets(taskcluster_secret,
                          config.PROJECT_NAME,
                          required=('STATIC_ANALYSIS_NOTIFICATIONS', ),
                          taskcluster_client_id=taskcluster_client_id,
                          taskcluster_access_token=taskcluster_access_token,
                          )

    init_logger(config.PROJECT_NAME,
                PAPERTRAIL_HOST=secrets.get('PAPERTRAIL_HOST'),
                PAPERTRAIL_PORT=secrets.get('PAPERTRAIL_PORT'),
                SENTRY_DSN=secrets.get('SENTRY_DSN'),
                MOZDEF=secrets.get('MOZDEF'),
                )

    w = Workflow(cache_root,
                 secrets['STATIC_ANALYSIS_NOTIFICATIONS'],
                 taskcluster_client_id,
                 taskcluster_access_token,
                 )

    for commit in REGEX_COMMIT.findall(commits):
        w.run(*commit)


if __name__ == '__main__':
    main()

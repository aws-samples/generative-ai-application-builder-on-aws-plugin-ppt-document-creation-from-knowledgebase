# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

# from bisheng import jinja_env

_TEMPLATE_ROOT = "summary"
_TEMPLATE_FILE_NAME = "summary.md.jinja"


def create_markdown_summary():
    pass


def _write_summary(path: str, summary: str):
    with open(path, "w+") as f:
        f.write(summary)

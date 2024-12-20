# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from bisheng.prompting.base_response import BaseResponse


class GaabResponse(BaseResponse):

    sources: str

    def to_json(self):
        return {
            "response": self.response,
            "rationale": self.rationale,
            "sources": self.sources,
        }

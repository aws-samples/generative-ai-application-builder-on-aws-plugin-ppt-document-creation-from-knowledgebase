# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseResponse(BaseModel, ABC):

    rationale: str
    response: str
    sources: str

    @abstractmethod
    def to_json(self):
        pass

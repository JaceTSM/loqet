"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""


class LoqetDecryptionException(Exception):
    pass


class LoqetContextConflictException(Exception):
    pass


class LoqetInvalidConfigException(Exception):
    pass


class LoqetInvalidContextException(Exception):
    pass


class LoqInvalidFileException(Exception):
    pass


class LoqetInvalidArgumentException(Exception):
    pass

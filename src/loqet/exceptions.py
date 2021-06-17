"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""


############################
# Loqet Context Exceptions #
############################

class LoqetContextException(Exception):
    pass


class LoqetContextConflictException(LoqetContextException):
    pass


class LoqetInvalidConfigException(LoqetContextException):
    pass


class LoqetInvalidContextException(LoqetContextException):
    pass


class LoqetNoSetContextException(LoqetContextException):
    pass


####################
# Loqet Exceptions #
####################

class LoqetException(Exception):
    pass


class LoqetDecryptionException(LoqetException):
    pass


class LoqInvalidFileException(LoqetException):
    pass


class LoqetInvalidArgumentException(LoqetException):
    pass

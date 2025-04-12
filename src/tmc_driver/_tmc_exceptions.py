"""Exceptions module"""

class TmcException(Exception):
    """Base class for all TMC exceptions"""
    pass

class TmcDriverException(TmcException):
    """Base class for all TMC driver exceptions"""
    pass

class TmcComException(TmcException):
    """Base class for all TMC communication exceptions"""
    pass

class TmcMotionControlException(TmcException):
    """Base class for all TMC motion control exceptions"""
    pass

class TmcEnableControlException(TmcException):
    """Base class for all TMC enable control exceptions"""
    pass

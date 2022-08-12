class GoiferError(Exception):
    """
    General goifer error class to provide a superclass for all other errors
    """


class NoMoreRecordsError(GoiferError):
    """
    This error is raised if all records have been loaded (or no records are
    present)
    """


class ConfigError(GoiferError):
    """
    This error is raised if the something is wrong with the config (e.g. missing elements).
    """


class GoiferWarning(Warning):
    """
    General goifer warning class to provide a superclass for all warnings
    """

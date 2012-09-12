#!/usr/bin/env python
from __future__ import unicode_literals

"""
Part of a webcitation.org bot
(C) Legoktm, 2012 under the MIT License
This portion has various error classes.
"""

class CitationdotOrgError(Exception):
    """Any error with webcitation.org"""
    
class ArchivingFailed(CitationdotOrgError):
    """When archiving with webcitation.org fails."""

class MYSQLError(Exception):
    """Any error with mysql"""

class NoTableError(MYSQLError):
    """When the table provided doesn't exist"""
import enum

class NotificationLevel(str, enum.Enum):
    WARNING       = "WARNING" 
    CRITICAL      = "CRITICAL"

class AuthStatus(str, enum.Enum):
    AUTHORIZED      = 'AUTHORIZED'
    UNAUTHORIZED    = 'UNAUTHORIZED'
    AUTHENTICATED   = 'AUTHENTICATED'
    UNAUTHENTICATED = 'UNAUTHENTICATED'
    FORBIDDEN       = 'FORBIDDEN'
    SUCCESS         = 'SUCCESS'
    ERROR           = 'ERROR'
    PENDING         = 'PENDING'
    INPROGRESS      = 'IN_PROGRESS'
    COMPLETED       = 'COMPLETED'
    INVALID         = 'INVALID'
    VALID           = 'VALID'
    ACTIVE          = 'ACTIVE'
    INACTIVE        = 'INACTIVE'
    BLOCKED         = 'BLOCKED'
    EXPIRED         = 'EXPIRED'

class SettingType(enum.Enum):
    STR  = "STR"
    BOOL = "BOOL"
    INT  = "INT"
    DICT = "DICT"
    LIST = "LIST"
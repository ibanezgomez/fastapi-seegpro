import enum

class NotificationLevel(str, enum.Enum):
    WARNING       = "WARNING" 
    CRITICAL      = "CRITICAL"

class ScanStatus(str, enum.Enum):
    UNKNOWN       = "UNKNOWN" 
    PREREGISTERED = "PREREGISTERED"
    ASSIGNED      = "ASSIGNED"
    CONFIGURING   = "CONFIGURING"
    FIN_ERROR     = "FIN_ERROR"
    PROGRESS      = "PROGRESS"
    FIN_SUCCESS   = "FIN_SUCCESS"

class ScanGlobalStatus(str, enum.Enum):
    FIN_ERROR     = "FIN_ERROR"
    PROGRESS      = "PROGRESS"
    FIN_SUCCESS   = "FIN_SUCCESS"

class BulkScanGlobalStatus(str, enum.Enum):
    PROGRESS      = "PROGRESS"
    FIN_SUCCESS   = "FIN_SUCCESS"

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

class SeverityRisk(enum.Enum):
    HIGH            = 'HIGH' 
    MEDIUM          = 'MEDIUM'
    LOW             = 'LOW'

class ReportType(enum.Enum):
    RAW = "raw"
    FORMATTED = "formatted"

class ResultFormat(enum.Enum):
    JSON  = "json"
    XML   = "xml"
    SARIF = "sarif"

class SettingType(enum.Enum):
    STR  = "STR"
    BOOL = "BOOL"
    INT  = "INT"
    DICT = "DICT"
    LIST = "LIST"
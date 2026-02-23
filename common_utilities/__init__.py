#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import enum


#<==================================================================================================>
#                                   ANGELFUND CONFIG
#                                   NEVER CHANGE THIS
#<==================================================================================================>
class CONSTANT(enum.Enum):
    EMAIL_REGION = "us-east-1"
    PASSWORD_RESET_LINK_AGE = "500"
    ACCESS_KEY = "***REMOVED***"
    MAIN_ML_SERVER = "http://52.9.228.194/"
    TEST_SERVER_DOMAIN = "http://***REMOVED***"
    ML_SERVER_X_AUTH_KEY = "\')*9s`\\+Ex*M,$<W"
    LOG_FILE = "/var/log/angelfund/angelfund.log"
    TEST_ML_SERVER = "http://***REMOVED***/ml/api/v1"
    MAIN_SERVER_DOMAIN = "https://www.angelfund.ai"
    EMAIL_SENDER = "Angelfund.ai <noreply@angelfund.ai>"
    LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
    EMAIL_SENDER_HELLO = "Angelfund.ai <hello@angelfund.ai>"
    ACCESS_VALUE = "***REMOVED***"
    RITEKIT_KEY = "***REMOVED***"
    SECRET_KEY = "***REMOVED***"
    JWT_SECRET_KEY = "***REMOVED***{V:'4\ea(>h&@?2'K-+?S,e_$>~)Byp9k*-"
    ANONYMOUS_PP = "https://angelfund-profile-pics.s3-us-west-1.amazonaws.com/anonymous.png"
    TEST_DB_CLUSTER = "mongodb://***REMOVED***:***REMOVED***@***REMOVED***/admin"
    SECONDARY_DB_CLUSTER = "mongodb://***REMOVED***:***REMOVED***@***REMOVED***/admin"
    PRIMARY_DB_CLUSTER = "mongodb://***REMOVED***:***REMOVED***@***REMOVED***/admin"
    CURRENT_DATABASE = TEST_DB_CLUSTER
    CURRENT_ML_SERVER = TEST_ML_SERVER
    CURRENT_SERVER = TEST_SERVER_DOMAIN
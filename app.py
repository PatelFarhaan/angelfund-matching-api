#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
import logging
import datetime
from project import app
from common_utilities import CONSTANT


#<==================================================================================================>
#                                      EXECUTION FILE
#<==================================================================================================>
if __name__ == "__main__":
    logging.basicConfig(filemode='a',
                        level=logging.DEBUG,
                        datefmt='%m-%d %H:%M',
                        format=CONSTANT.LOG_FORMAT.value,
                        filename=CONSTANT.LOG_FILE.value)
    logging.getLogger("sys").setLevel(logging.CRITICAL)
    logging.getLogger("boto").setLevel(logging.CRITICAL)
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("werkzeug").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.CRITICAL)

    logger = logging.getLogger(__name__)
    logger.info(f"flask reserver started at {datetime.datetime.utcnow()}")
    app.run(host='127.0.0.1', port=5000, debug=False)
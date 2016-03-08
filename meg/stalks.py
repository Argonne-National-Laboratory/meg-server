from collections import namedtuple

from celery.utils.log import get_task_logger
from gcm import GCM

logger = get_task_logger(__name__)


def create_celery_routes(celery, cfg):
    @celery.task
    def transmit_gcm_id(gcm_iid, id):
        gcm = GCM(cfg.config.gcm_api_key)
        data = {"message_id": id}
        logger.info("Transmit id: {} to phone with iid: {}".format(id, gcm_iid))
        response = gcm.json_request(registration_ids=[gcm_iid], data=data)
        if 'errors' in response:
            transmit_gcm_id.retry(
                args=[gcm_iid, uuid], countdown=cfg.config.timeout.gcm_msg
            )

    CeleryTasks = namedtuple('CeleryTasks', ['transmit_gcm_id'])
    return CeleryTasks(transmit_gcm_id)

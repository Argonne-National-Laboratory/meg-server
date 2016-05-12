from collections import namedtuple

from celery.utils.log import get_task_logger
from gcm import GCM

from meg import constants


def create_celery_routes(celery, cfg):
    logger = get_task_logger(__name__)

    # XXX This is kinda a thing. If we have a item that is not retried then
    # we will not be able to deliver a message. So eventually we should probably
    # have a cron task that takes messages that have failed their retries and
    # continually resend them
    @celery.task(max_retries=cfg.config.celery.transmit_gcm_id.retries)
    def transmit_gcm_id(gcm_iid, id, action):
        if action not in constants.PHONE_ACTIONS:
            raise Exception("Choose an action that is one of {}".format(PHONE_ACTIONS))
        gcm = GCM(cfg.config.gcm_api_key)
        data = {"message_id": id, "action": action}
        logger.info("Transmit id: {} to phone with iid: {}".format(id, gcm_iid))
        response = gcm.json_request(registration_ids=[gcm_iid], data=data)
        if 'errors' in response:
            logger.warn("Error found in response: {}".format(response))
            transmit_gcm_id.retry(
                args=[gcm_iid, id, action], countdown=cfg.config.celery.transmit_gcm_id.timeout
            )
        else:
            logger.debug("Message transmitted successfully response: {}".format(response))

    @celery.task(max_retries=cfg.config.celery.remove_key_data.retries)
    def remove_key_data(gcm_iid):
        gcm = GCM(cfg.config.gcm_api_key)
        data = {"action": "revoke"}
        response = gcm.json_request(registration_ids=[gcm_iid], data=data)
        if 'errors' in response:
            remove_key_data.retry(
                args=[gcm_iid], countdown=cfg.config.celery.remove_key_data.timeout
            )

    CeleryTasks = namedtuple('CeleryTasks', ['transmit_gcm_id'])
    return CeleryTasks(transmit_gcm_id)

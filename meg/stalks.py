from collections import namedtuple

from gcm import GCM


def create_celery_routes(celery, cfg):
    @celery.task
    def transmit_gcm_uuid(gcm_iid, uuid):
        gcm = GCM(cfg.config.gcm_api_key)
        data = {"message_id": uuid}
        response = gcm.json_request(registration_ids=[gcm_iid], data=data)
        if 'errors' in response:
            transmit_gcm.retry(
                args=[gcm_iid, uuid], countdown=cfg.config.timeout.gcm_msg
            )

    CeleryTasks = namedtuple('CeleryTasks', ['transmit_gcm_uuid'])
    return CeleryTasks(transmit_gcm_uuid)

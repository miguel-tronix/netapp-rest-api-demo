# -*- coding: utf-8 -*-
import os
import yaml
import logging
import logging.config


def update_old_with_new(obj_tmpl, old_obj, new_obj):

    log = setup_logging(__name__)

    log.debug("OLDCVT: %s" % old_obj)
    log.debug("NEWCVT: %s" % new_obj)
    log.debug("TMPLTCVT: %s" % obj_tmpl)

    if type(old_obj) is not dict or type(new_obj) is not dict:
        return None

    if obj_tmpl is None:
        obj_tmpl = {}
        tmp = list(set(old_obj.keys()) | set(new_obj.keys()))
        for k in tmp:
            obj_tmpl[k] = None

    if type(obj_tmpl) is not dict:
        obj_tmpl = obj_tmpl.value

    for key in list(obj_tmpl.keys()):
        if key in new_obj and new_obj.get(key) is not None\
        and new_obj[key] != '':
            if type(new_obj[key]) is dict:
                old_obj[key] =\
                update_old_with_new(
                    obj_tmpl[key],
                     old_obj.get(key) if not None else {},
                      new_obj[key]
                    )
            else:
                if type(new_obj[key]) is list:
                    old_obj[key] = list(set(old_obj[key]) | set(new_obj[key]))
                else:
                    old_obj[key] = new_obj[key]

    return old_obj


def setup_logging(
        logger_name=__name__,
        default_path='logging.yml',
        default_level=logging.INFO,
        env_key='LOG_CFG'
        ):
            path = default_path
            value = os.getenv(env_key, None)
            if value:
                path = value
            if os.path.exists(path):
                with open(path, 'rt') as cfg:
                    config = yaml.safe_load(cfg.read())
                    logging.config.dictConfig(config)
            else:
                logging.basicConfig(level=default_level)

            return logging.getLogger(logger_name)



from __future__ import annotations

import logging
import typing

from ._target_object import _TargetObject


class _LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger, obj_list: tuple[_TargetObject, ...] | None = None):
        super().__init__(logger)
        self.obj_list = obj_list

    def nest_obj_logger(self, obj: typing.Any) -> _LoggerAdapter:
        obj_id = str(id(obj))
        obj_module = ''
        obj_qualname = ''

        if hasattr(obj, '__module__'):
            obj_module = obj.__module__
        if hasattr(obj, '__qualname__'):
            obj_qualname = obj.__qualname__
        if hasattr(obj, '__class__'):
            obj_module = obj.__module__
            obj_qualname = obj.__class__.__qualname__

        obj_list = tuple(
            (
                *(self.obj_list if self.obj_list is not None else ()),
                _TargetObject(
                    obj_id=obj_id,
                    obj_module=obj_module,
                    obj_qualname=obj_qualname,
                ),
            )
        )

        return _LoggerAdapter(
            logger=self.logger,
            obj_list=obj_list,
        )

    def process(self, msg: str, kwargs: dict[str, typing.Any]):  # type: ignore
        extra = {"obj_list": self.obj_list}

        if 'params_please' in kwargs:
            extra['params_please'] = kwargs['params_please']
            del kwargs['params_please']

        if 'extra' not in kwargs:
            kwargs['extra'] = extra
        else:
            kwargs['extra'] |= extra

        return (msg, kwargs)

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class _TargetObject:
    obj_id: str
    obj_module: str
    obj_qualname: str

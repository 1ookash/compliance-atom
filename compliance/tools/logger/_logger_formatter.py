# mypy: ignore-errors
import copy
import logging
import textwrap
import time

from compliance.tools import printer


class _LoggerFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            style='{',
            validate=True,
            fmt='{asctime} {levelname} {name}{obj_list}\n\t: {msg}',
            defaults={'obj_list': ''},
        )
        self.converter = time.gmtime

    def format(self, record: logging.LogRecord) -> str:
        copy_f = False

        if '\n' in record.msg:
            record = copy.copy(record) if not copy_f else record
            copy_f = True

            record.msg = textwrap.indent(textwrap.dedent(record.msg).strip(' \t\r\n'), '\t\t')
            record.msg = '(\n{msg}\n\t)'.format(msg=record.msg)

        if hasattr(record, 'obj_list') and getattr(record, 'obj_list') is not None:
            record = copy.copy(record) if not copy_f else record
            copy_f = True

            setattr(
                record,
                'obj_list',
                (
                    ''.join(
                        (
                            '\n\t{obj_module}.{obj_qualname}|{obj_id}'.format(
                                obj_module=obj.obj_module,
                                obj_qualname=obj.obj_qualname,
                                obj_id=obj.obj_id,
                            )
                            for obj in getattr(record, 'obj_list')
                        )
                    )
                ),
            )

        if hasattr(record, 'params_please'):
            record = copy.copy(record) if not copy_f else record
            copy_f = True

            for name, value in getattr(record, 'params_please').items():
                if isinstance(value, Exception):
                    value = printer.Printer.pretty_print(value)

                else:
                    value = str(value)

                if '\n' in value:
                    value = textwrap.indent(textwrap.dedent(value).strip(' \t\r\n'), '\t\t')
                    value = '(\n{value}\n\t)'.format(value=value)

                record.msg += '\n\t, {name} = {value}'.format(
                    name=name,
                    value=value,
                )

        return super().format(record)

import os
import platform
import pprint
import sys


class Printer:
    @staticmethod
    def get_platform_specs(list_modules_f: bool = True) -> dict[str, str | int | float]:
        specs: dict[str, str | int | float] = {}

        specs["platform"] = platform.platform()
        specs["system"] = platform.system()
        specs["executable"] = sys.executable
        specs["python_version"] = sys.version
        specs["python_path"] = "\n".join((path for path in sys.path if len(path) > 0))
        specs["cwd"] = os.getcwd()

        if list_modules_f:
            modules = tuple(sys.modules.items())
            modules_builtin = set(sys.builtin_module_names) | set(sys.stdlib_module_names)
            modules = tuple(
                (
                    (name, module)
                    for (name, module) in modules
                    if hasattr(module, "__version__")
                    and name not in modules_builtin
                    and module.__name__ not in modules_builtin
                    and name.split(".")[0] == name
                )
            )

            specs["modules"] = "\n".join(
                (f"{name}: {module.__version__}" for (name, module) in modules)
            )

        return specs

    @staticmethod
    def pretty_print(obj: object, depth: int | None = None, width: int = 1) -> str:
        printer = pprint.PrettyPrinter(
            depth=depth,
            compact=False,
            width=width,
            sort_dicts=False,
        )
        obj_text = printer.pformat(obj)

        return obj_text

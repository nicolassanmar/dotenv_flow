import os

import warnings
from pathlib import Path

from typing import Any, Mapping, Sequence, Optional

from dotenv import load_dotenv, find_dotenv

__all__ = ["dotenv_flow"]


_DEFAULTS = [".env.defaults", ".env"]


def dotenv_flow(
    env: Optional[str] = os.getenv("PY_ENV", ...),
    base_path: Optional[os.PathLike] = None,
    load_global_env: Optional[bool] = False,
    **kwargs: Mapping[str, Any],
) -> Sequence[str]:
    """
    Load dotenv files based on the value of the PY_ENV variable, if set.
    Values in more specific files override previous values.
    Files have 3 flavors:
        - global: (ex: .env) that should be committed to version control
        - public (ex: .env.dev) that should be committed to version control
        - private (ex: .env.dev.local) that has preference over the previous one, if present

    dotenv files are searched and loaded with python-dotenv

    :param env: The name of the environment. It can be set to None explicitly to remove the warning and run with defaults only.
    :param base_path: If provided, the base path to load the files from. Otherwise, the current working directory is used.
    :param load_global_env: Whether the '.env' file is loaded or not.
    :return: a list with the paths of the files loaded
    """

    use_cwd = base_path is None

    names = [*_DEFAULTS]
    if env not in (..., None):
        names.append(f".env.{env}")
    elif env is not None:
        warnings.warn("no env selected, using defaults only")

    if load_global_env:
        names.append(".env")

    loaded = {}
    for name in reversed(names):
        for env_file in (f"{name}.local", name):
            if not use_cwd:
                env_file = Path(base_path) / env_file

            dotenv_path = find_dotenv(env_file, usecwd=use_cwd)
            if dotenv_path:
                loaded[dotenv_path] = load_dotenv(
                    dotenv_path,
                    **kwargs,
                )
    return [e for e in loaded if loaded[e]]

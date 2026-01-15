"""Password policy utilities."""
from __future__ import annotations

import re


def validate_password_strength(password: str) -> None:
    """Validate password against policy."""
    if not password:
        raise ValueError("Informe uma senha.")

    if len(password) < 8:
        raise ValueError("A senha deve ter no mínimo 8 caracteres.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("A senha é muito longa. Use até 72 caracteres.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("A senha deve conter pelo menos 1 letra maiúscula.")

    if not re.search(r"\d", password):
        raise ValueError("A senha deve conter pelo menos 1 número.")

    if not re.search(r"[^\w\s]", password):
        raise ValueError("A senha deve conter pelo menos 1 caractere especial (ex.: !@#$%).")

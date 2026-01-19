from dataclasses import dataclass

from client_repository import ClientRepository
from access_code_repository import AccessCodeRepository
from passwords import hash_password, verify_password


MAX_FAILED_ATTEMPTS = 3


@dataclass
class AuthResult:
    success: bool
    message: str
    is_new_user: bool = False


class AuthService:
    def __init__(
        self,
        client_repo: ClientRepository,
        access_code_repo: AccessCodeRepository,
    ):
        self.client_repo = client_repo
        self.access_code_repo = access_code_repo

    def authenticate(
        self,
        client_id: str,
        password: str,
        access_code: str | None = None,
    ) -> AuthResult:
        """
        Autenticación principal.

        - Si el client_id NO existe -> REGISTRO (requiere access_code)
        - Si el client_id existe     -> LOGIN
        """

        client = self.client_repo.get_by_client_id(client_id)

        # ======================================================
        # REGISTRO (cliente no existe)
        # ======================================================
        if client is None:
            if not access_code:
                return AuthResult(
                    False,
                    "Se requiere access code para el registro."
                )

            if not self.access_code_repo.exists_and_unused(access_code):
                return AuthResult(
                    False,
                    "Access code inválido o ya usado."
                )

            # Crear cliente
            password_hash = hash_password(password)

            self.client_repo.create(
                client_id=client_id,
                password_hash=password_hash,
                status="ACTIVO",
            )

            # Consumir access code
            self.access_code_repo.mark_as_used(access_code, client_id)

            return AuthResult(
                True,
                "Registro completado correctamente.",
                is_new_user=True
            )

        # ======================================================
        # LOGIN (cliente existe)
        # ======================================================
        if client["status"] == "BLOCK":
            return AuthResult(
                False,
                "Cuenta bloqueada. Contacta con el administrador."
            )

        if not verify_password(password, client["password_hash"]):
            self._handle_failed_attempt(client_id, client)
            return AuthResult(False, "Password incorrecta.")

        # Login correcto
        self.client_repo.reset_failed_attempts(client_id)

        return AuthResult(True, "Autenticación correcta.")

    # ------------------------------------------------------
    # Helpers
    # ------------------------------------------------------
    def _handle_failed_attempt(self, client_id: str, client: dict):
        """
        Incrementa intentos fallidos y bloquea si se supera el máximo.
        """
        self.client_repo.increment_failed_attempts(client_id)

        failed_attempts = client["failed_attempts"] + 1
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            self.client_repo.update_status(client_id, "BLOCK")


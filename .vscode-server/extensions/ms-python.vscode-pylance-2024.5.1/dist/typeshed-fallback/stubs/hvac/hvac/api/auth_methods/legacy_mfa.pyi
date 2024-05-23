from _typeshed import Incomplete

from hvac.api.vault_api_base import VaultApiBase

SUPPORTED_MFA_TYPES: Incomplete
SUPPORTED_AUTH_METHODS: Incomplete

class LegacyMfa(VaultApiBase):
    def configure(self, mount_point, mfa_type: str = "duo", force: bool = False): ...
    def read_configuration(self, mount_point): ...
    def configure_duo_access(self, mount_point, host, integration_key, secret_key): ...
    def configure_duo_behavior(
        self, mount_point, push_info: Incomplete | None = None, user_agent: Incomplete | None = None, username_format: str = "%s"
    ): ...
    def read_duo_behavior_configuration(self, mount_point): ...

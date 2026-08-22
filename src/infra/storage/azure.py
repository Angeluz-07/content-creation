# storage/azure_client.py
import os
from datetime import datetime, timedelta, timezone
from typing import Protocol
from azure.storage.blob import BlobServiceClient, CorsRule, generate_blob_sas, BlobSasPermissions

class StorageServiceProtocol(Protocol):
    def generate_upload_signed_url(
        self, file_name: str, file_type: str, expires_in_minutes: int = 15
    ) -> dict:
        """Genera la URL firmada para subidas mediante PUT y retorna {'uploadUrl': ..., 'fileKey': ...}"""
        pass

    def generate_download_signed_url(
        self, file_key: str, expires_in_minutes: int = 15
    ) -> str:
        """Genera la URL firmada para lectura/descarga de un archivo existente"""
        pass


class AzureStorageService(StorageServiceProtocol):
    def __init__(self, connection_string: str, container_name: str):
        self.container_name = container_name
        self.client = BlobServiceClient.from_connection_string(connection_string)
        self._ensure_container_and_cors()

    def _ensure_container_and_cors(self):
        # 1. Crear el contenedor si no existe
        container_client = self.client.get_container_client(self.container_name)
        if not container_client.exists():
            container_client.create_container(public_access="blob")

        # 2. Configurar reglas CORS en Azurite / Azure Blob Storage
        cors_rule = CorsRule(
            allowed_origins=['*'],  # Permite peticiones desde localhost:5173
            allowed_methods=['GET', 'PUT', 'OPTIONS', 'HEAD'],
            allowed_headers=['*'],
            exposed_headers=['*'],
            max_age_in_seconds=3600
        )
        try:
            self.client.set_service_properties(cors=[cors_rule])
        except Exception as e:
            print(f"Warning al aplicar reglas CORS: {e}")

    def generate_download_signed_url(
        self, file_key: str, expires_in_minutes: int = 15
    ) -> str:
        sas_token = generate_blob_sas(
            account_name=self.client.account_name,
            container_name=self.container_name,
            blob_name=file_key,
            account_key=self.client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
        )

        blob_client = self.client.get_blob_client(
            container=self.container_name, blob=file_key
        )
        return f"{blob_client.url}?{sas_token}"

    def generate_upload_signed_url(
        self, file_name: str, file_type: str, expires_in_minutes: int = 15
    ) -> dict:
        file_key = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{file_name}"

        sas_token = generate_blob_sas(
            account_name=self.client.account_name,
            container_name=self.container_name,
            blob_name=file_key,
            account_key=self.client.credential.account_key,
            permission=BlobSasPermissions(write=True, create=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
        )

        blob_client = self.client.get_blob_client(
            container=self.container_name, blob=file_key
        )
        raw_url = f"{blob_client.url}?{sas_token}"

        # 🟢 TRADUCCIÓN TRANSPARENTE SOLO PARA ENTORNO LOCAL
        # Si la URL contiene el endpoint interno de Azurite, la exponemos como 127.0.0.1 hacia el navegador.
        # En Producción (https://*.blob.core.windows.net) este 'replace' no hace nada y pasa intacto.
        public_upload_url = raw_url.replace(
            "http://azurite_storage:10000", "http://localhost:10000"
        ).replace("http://azurite:10000", "http://localhost:10000")

        return {"uploadUrl": public_upload_url, "fileKey": file_key}

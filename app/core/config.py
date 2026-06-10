from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación usando variables de entorno.
    
    Gestiona las claves API y tokens necesarios para la integración con
    servicios externos como Anthropic y GitHub. Los valores se cargan desde
    un archivo .env en la raíz del proyecto.
    
    Attributes:
        ANTHROPIC_API_KEY (str): Clave API para autenticación en Anthropic.
        GITHUB_TOKEN (str): Token personal de GitHub para acceso a la API.
        GITHUB_WEBHOOK_SECRET (str): Secreto para validar webhooks de GitHub. Opcional.
    """
    ANTHROPIC_API_KEY: str
    GITHUB_TOKEN: str
    GITHUB_WEBHOOK_SECRET: str = ""  # Opcional en desarrollo

    class Config:
        """Configuración de Pydantic para la carga de variables de entorno.
        
        Define cómo se deben cargar y procesar las variables de entorno,
        especificando la ubicación y codificación del archivo .env.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
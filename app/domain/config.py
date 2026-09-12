from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = find_dotenv()
load_dotenv(env_file)


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=env_file)
    
    RANDOM_SEED: int
    

settings = Settings()

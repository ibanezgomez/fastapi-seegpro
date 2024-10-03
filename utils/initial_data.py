import json
from utils.config import config
from sqlalchemy import exc
from services.auth import pwd_context
from models.base import SQLModel
from models.example import ExampleModel
from models.setting import SettingModel
from models.client import ClientModel
from utils.logger import log
from utils.session import SessionFactory, getEngine

def initAndPopulate():

    """Create al the tables related with models in models folder """
    try:
        session = SessionFactory()
        engine  = getEngine()

        #Create tables
        SQLModel.metadata.create_all(engine)

        #Populate initial data with settings file
        initial_data_objects = {"SettingModel": []}
        try:
            with open(f"settings/settings-{config.env.lower()}.json") as file: settings = json.load(file)
            for id in settings:
                value = settings[id]
                initial_data_objects["SettingModel"].append(SettingModel(id=id, value=value))
        except Exception as e:
            log.error("Unable to load settings from JSON: %s" % e, action="[initAndPopulate]")

        #Populate initial data from this file
        initial_data_objects.update(initialData)

        for model in initial_data_objects:
            for o in initial_data_objects[model]:
                try:
                    log.info("Añado: %s" % o, action="[initAndPopulate]")
                    session.add(o)
                    session.commit()
                except (exc.IntegrityError, exc.PendingRollbackError) as e:
                    log.debug("%s: %s exists in database and not would be created" % (str(type(e).__name__), o), action="[initAndPopulate]")
                    session.rollback()
                except Exception as e:
                    log.debug("Unexpected error adding %s: %s" % (o, str(type(e).__name__)), action="[initAndPopulate]")
        return True
    except Exception as e:
        print(e)
        log.error("Unable to made initAndPopulate operation: %s" % (str(type(e).__name__)), action="[initAndPopulate]")
        session.close()
        return False

##### INITIAL DATA #####
initialData = {
    "ClientModel": [
        ClientModel(id=config.secrets.default_user, desc="Usuario default", provider="local", permissions={}, 
                    hashed_password=pwd_context.hash(config.secrets.default_pass))
    ],
    "ExampleModel": [
        ExampleModel(id=1, name="Example1", description="Is an example", active=True)
    ]
}


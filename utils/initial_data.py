import json
from utils.config import config
from sqlalchemy import exc
from models.base import SQLModel
from models.example import ExampleModel
from models.setting import SettingModel
from models.user import UserModel
from utils.logger import log
from utils.session import SessionFactory, getEngine
from utils.crypto import bcrypt_hash

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
    "UserModel": [
        UserModel(id="jmiralco", name="Jordi", surname="Miralles", roles=["ADMIN", "USER"], hashed_password=bcrypt_hash("jmiralco123")),
        UserModel(id="sibanego", name="Samuel", surname="Ibañez", roles=["USER"], hashed_password=bcrypt_hash("sibanego123"))
    ],
    "ExampleModel": [
        ExampleModel(id=1, name="Example1", description="Is an example", active=True),
        ExampleModel(id=2, name="Example2", description="Is an example new", active=True),
        ExampleModel(id=3, name="Example3", description="Is another example", active=False),
        ExampleModel(id=4, name="Example4", description="Is a new example", active=True),
        ExampleModel(id=5, name="Example5", description="Is an example? Maybe", active=False),
        ExampleModel(id=6, name="Example6", description="Is a good example", active=True),
        ExampleModel(id=7, name="Example7", description="Is an example interesting", active=True),
        ExampleModel(id=8, name="Example8", description="Is an example of how to make examples", active=True),
        ExampleModel(id=9, name="Example9", description="Example is", active=False),
        ExampleModel(id=10, name="Example10", description="Not an example", active=True),
    ]
}


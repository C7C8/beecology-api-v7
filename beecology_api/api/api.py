from flask_restplus import Api

# TODO Add default error handlers
api = Api(version="1.0.3",
          title="Beecology API",
          description="Processes requests to upload and download beecology data.",
          contact="beecologyproject@wpi.edu")

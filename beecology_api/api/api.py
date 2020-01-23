from flask_restplus import Api

# TODO Add default error handlers
api = Api(version="1.0.0", title="Beecology data API", description="Processes requests to upload and download "
                                                                   "beecology data")

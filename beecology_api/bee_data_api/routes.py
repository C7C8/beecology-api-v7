from flask_restplus import Namespace

from .endpoints import *

#########################################################
#                      API ROUTES                       #
#########################################################

def setup_routes(ns: Namespace):
	ns.add_resource(IsConnected, "/isConnected")

	# Bee data
	ns.add_resource(Beedex, "/beedex/<int:id>")
	ns.add_resource(Beedex, "/beedex")
	ns.add_resource(BeeRecord, "/beerecord/<int:id>")
	ns.add_resource(BeeRecordsList, "/beerecords/<int:page>")
	ns.add_resource(BeeVisRecords, "/beevisrecords")
	ns.add_resource(BeeUserRecords, "/beerecorduser")
	ns.add_resource(RecordData, "/record")
	ns.add_resource(NoElevationData, "/noelevationrecords")

	# Flower data -- don't look at me like that! I didn't write the API interface spec!
	ns.add_resource(Flowerdex, "/addflower")  # POST new flower.
	ns.add_resource(Flowerdex, "/flowerdex")  # GET or POST flower.
	ns.add_resource(Flowerdex, "/flowerdex/<int:id>")  # GET or DELETE flower entry
	ns.add_resource(Flowerdex, "/deleteflower/<int:id>")  # DELETE flower.
	ns.add_resource(FlowerList, "/flowerlist")  # Legacy support for flowerlist endpoint
	ns.add_resource(FlowerShapes, "/flowershapes")
	ns.add_resource(FlowerShapes, "/flowercolors")  # Not a typo, these have the same handler...
	ns.add_resource(UnmatchedFlowers, "/unmatched_flowers")

	# Media upload
	ns.add_resource(UploadImage, "/uploadImage64")
	ns.add_resource(UploadVideo, "/uploadVideo")

	# Login/refresh/logout
	ns.add_resource(Enroll, "/enroll")
	ns.add_resource(Refresh, "/refresh")
	ns.add_resource(Unenroll, "/unenroll")

	# News
	ns.add_resource(UpdateBioCSNews, "/update_biocsnews")
	ns.add_resource(GetBioCSNews, "/biocsnews")
	ns.add_resource(UpdateNews, "/update_news")
	ns.add_resource(GetNews, "/news")

	# Admin
	ns.add_resource(VerifyAdmin, "/verifyAdmin")

########################################################

#!/usr/bin/env python3
from diagrams import Cluster, Diagram, Edge
from diagrams.gcp.compute import AppEngine
from diagrams.gcp.storage import GCS
from diagrams.gcp.database import SQL
from diagrams.generic.device import Tablet

with Diagram("Givesome Architecture", show=False):
    end_user = Tablet("Users")
    with Cluster("Cloud Run (iowa-1)"):
        app = [
            AppEngine("App"),
            AppEngine("App"),
            AppEngine("App"),
        ]
    with Cluster("Cloud Storage (iowa-1)"):
        storage = GCS("Media Bucket")
    with Cluster("Cloud SQL (iowa-1)"):
        db = SQL("Database")
    app >> db
    app >> storage
    end_user >> Edge(colour="black") >> app

from flask import current_app as app
from .models import Region

@app.context_processor
def get_regions_list():
    return dict(regions=Region.query.all())

from wtforms import Form
from wtforms_alchemy import model_form_factory


from apps.models import *


ModelForm = model_form_factory(Form)


class LocationForm(ModelForm):
    class Meta:
        model = Location
        
class AssetCategoryForm(ModelForm):
    class Meta:
        model = AssetCategory
        
class EmissionFactorsForm(ModelForm):
    class Meta:
        model = EmissionFactors
        
class CarbonEmissionForm(ModelForm):
    class Meta:
        model = CarbonEmission
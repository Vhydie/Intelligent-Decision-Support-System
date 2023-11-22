import json

from flask import request
from flask_restx import Api, Resource
from werkzeug.datastructures import MultiDict


from apps.api import blueprint
from apps.authentication.decorators import token_required

from apps.api.forms import *
from apps.models    import *

api = Api(blueprint)


@api.route('/locations/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@api.route('/locations/<string:model_id>/', methods=['GET', 'DELETE', 'PUT'])
class LocationRoute(Resource):
    def get(self, model_id: str = None):
        if model_id is None:
            all_objects = Location.query.all()
            output = [{'kode_lokasi': obj.kode_lokasi, 'nama_gedung': obj.nama_gedung, 'nama_ruang': obj.nama_ruang} for obj in all_objects]
        else:
            obj = Location.query.get(model_id)
            if obj is None:
                return {
                    'message': 'matching record not found',
                    'success': False
                }, 404
            output = {'kode_lokasi': obj.kode_lokasi, 'nama_gedung': obj.nama_gedung, 'nama_ruang': obj.nama_ruang}
        return {
            'data': output,
            'success': True
        }, 200

    @token_required
    def post(self):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}
        form = LocationForm(MultiDict(body_of_req))
        if form.validate():
            try:
                obj = Location(**body_of_req)
                db.session.add(obj)
                db.session.commit()
            except Exception as e:
                return {
                    'message': str(e),
                    'success': False
                }, 400
        else:
            return {
                'message': form.errors,
                'success': False
            }, 400
        return {
            'message': 'record saved!',
            'success': True
        }, 200

    @token_required
    def put(self, model_id: str):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}

        to_edit_row = Location.query.filter_by(kode_lokasi=model_id).first()

        if not to_edit_row:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404

        form = LocationForm(MultiDict(body_of_req), obj=to_edit_row)
        if not form.validate():
            return {
                'message': form.errors,
                'success': False
            }, 404

        for field, value in body_of_req.items():
            setattr(to_edit_row, field, value)
        db.session.commit()
        return {
            'message': 'record updated',
            'success': True
        }, 200

    @token_required
    def delete(self, model_id: str):
        to_delete = Location.query.filter_by(kode_lokasi=model_id)
        if to_delete.count() == 0:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404
        to_delete.delete()
        db.session.commit()
        return {
            'message': 'record deleted!',
            'success': True
        }, 200


@api.route('/asset_categories/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@api.route('/asset_categories/<string:model_id>/', methods=['GET', 'DELETE', 'PUT'])
class AssetCategoryRoute(Resource):
    def get(self, model_id: str = None):
        if model_id is None:
            all_objects = AssetCategory.query.all()
            output = [
                {
                    'kode_kategori': obj.kode_kategori,
                    'major_category': obj.major_category,
                    'major_category_name': obj.major_category_name,
                    'category': obj.category,
                    'category_name': obj.category_name,
                    'sub_category': obj.sub_category,
                    'sub_category_name': obj.sub_category_name,
                    'asset_ef': obj.asset_ef
                } for obj in all_objects
            ]
        else:
            obj = AssetCategory.query.get(model_id)
            if obj is None:
                return {
                    'message': 'matching record not found',
                    'success': False
                }, 404
            output = {
                'kode_kategori': obj.kode_kategori,
                'major_category': obj.major_category,
                'major_category_name': obj.major_category_name,
                'category': obj.category,
                'category_name': obj.category_name,
                'sub_category': obj.sub_category,
                'sub_category_name': obj.sub_category_name,
                'asset_ef': obj.asset_ef
            }
        return {
            'data': output,
            'success': True
        }, 200

    @token_required
    def post(self):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}
        form = AssetCategoryForm(MultiDict(body_of_req))
        if form.validate():
            try:
                obj = AssetCategory(**body_of_req)
                db.session.add(obj)
                db.session.commit()
            except Exception as e:
                return {
                    'message': str(e),
                    'success': False
                }, 400
        else:
            return {
                'message': form.errors,
                'success': False
            }, 400
        return {
            'message': 'record saved!',
            'success': True
        }, 200

    @token_required
    def put(self, model_id: str):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}

        to_edit_row = AssetCategory.query.filter_by(kode_kategori=model_id).first()

        if not to_edit_row:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404

        form = AssetCategoryForm(MultiDict(body_of_req), obj=to_edit_row)
        if not form.validate():
            return {
                'message': form.errors,
                'success': False
            }, 404

        for field, value in body_of_req.items():
            setattr(to_edit_row, field, value)
        db.session.commit()
        return {
            'message': 'record updated',
            'success': True
        }, 200

    @token_required
    def delete(self, model_id: str):
        to_delete = AssetCategory.query.filter_by(kode_kategori=model_id)
        if to_delete.count() == 0:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404
        to_delete.delete()
        db.session.commit()
        return {
            'message': 'record deleted!',
            'success': True
        }, 200


@api.route('/emission_factors/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@api.route('/emission_factors/<string:model_id>/', methods=['GET', 'DELETE', 'PUT'])
class EmissionFactorsRoute(Resource):
    def get(self, model_id: str = None):
        if model_id is None:
            all_objects = EmissionFactors.query.all()
            output = [
                {
                    'kode_ef': obj.kode_ef,
                    'nama_ef': obj.nama_ef,
                    'nilai_ef': obj.nilai_ef,
                    'tahun_relevansi_ef': obj.tahun_relevansi_ef
                } for obj in all_objects
            ]
        else:
            obj = EmissionFactors.query.get(model_id)
            if obj is None:
                return {
                    'message': 'matching record not found',
                    'success': False
                }, 404
            output = {
                'kode_ef': obj.kode_ef,
                'nama_ef': obj.nama_ef,
                'nilai_ef': obj.nilai_ef,
                'tahun_relevansi_ef': obj.tahun_relevansi_ef
            }
        return {
            'data': output,
            'success': True
        }, 200

    @token_required
    def post(self):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}
        form = EmissionFactorsForm(MultiDict(body_of_req))
        if form.validate():
            try:
                obj = EmissionFactors(**body_of_req)
                db.session.add(obj)
                db.session.commit()
            except Exception as e:
                return {
                    'message': str(e),
                    'success': False
                }, 400
        else:
            return {
                'message': form.errors,
                'success': False
            }, 400
        return {
            'message': 'record saved!',
            'success': True
        }, 200

    @token_required
    def put(self, model_id: str):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}

        to_edit_row = EmissionFactors.query.filter_by(kode_ef=model_id).first()

        if not to_edit_row:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404

        form = EmissionFactorsForm(MultiDict(body_of_req), obj=to_edit_row)
        if not form.validate():
            return {
                'message': form.errors,
                'success': False
            }, 404

        for field, value in body_of_req.items():
            setattr(to_edit_row, field, value)
        db.session.commit()
        return {
            'message': 'record updated',
            'success': True
        }, 200

    @token_required
    def delete(self, model_id: str):
        to_delete = EmissionFactors.query.filter_by(kode_ef=model_id)
        if to_delete.count() == 0:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404
        to_delete.delete()
        db.session.commit()
        return {
            'message': 'record deleted!',
            'success': True
        }, 200


@api.route('/carbon_emissions/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@api.route('/carbon_emissions/<int:model_id>/', methods=['GET', 'DELETE', 'PUT'])
class CarbonEmissionRoute(Resource):
    def get(self, model_id: int = None):
        if model_id is None:
            all_objects = CarbonEmission.query.all()
            output = [
                {
                    'id_aset': obj.id_aset,
                    'nomor_aset': obj.nomor_aset,
                    'kode_lokasi': obj.kode_lokasi,
                    'unit_kerja': obj.unit_kerja,
                    'kode_kategori': obj.kode_kategori,
                    'deskripsi': obj.deskripsi,
                    'tahun_perolehan': obj.tahun_perolehan,
                    'jumlah_unit': obj.jumlah_unit,
                    'energy': float(obj.energy),
                    'cost': float(obj.cost),
                    'carbon': float(obj.carbon)
                } for obj in all_objects
            ]
        else:
            obj = CarbonEmission.query.get(model_id)
            if obj is None:
                return {
                    'message': 'matching record not found',
                    'success': False
                }, 404
            output = {
                'id_aset': obj.id_aset,
                'nomor_aset': obj.nomor_aset,
                'kode_lokasi': obj.kode_lokasi,
                'unit_kerja': obj.unit_kerja,
                'kode_kategori': obj.kode_kategori,
                'deskripsi': obj.deskripsi,
                'tahun_perolehan': obj.tahun_perolehan,
                'jumlah_unit': obj.jumlah_unit,
                'energy': float(obj.energy),
                'cost': float(obj.cost),
                'carbon': float(obj.carbon)
            }
        return {
            'data': output,
            'success': True
        }, 200

    @token_required
    def post(self):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}
        form = CarbonEmissionForm(MultiDict(body_of_req))
        if form.validate():
            try:
                obj = CarbonEmission(**body_of_req)
                db.session.add(obj)
                db.session.commit()
            except Exception as e:
                return {
                    'message': str(e),
                    'success': False
                }, 400
        else:
            return {
                'message': form.errors,
                'success': False
            }, 400
        return {
            'message': 'record saved!',
            'success': True
        }, 200

    @token_required
    def put(self, model_id: int):
        try:
            body_of_req = request.form
            if not body_of_req:
                raise Exception()
        except Exception:
            if len(request.data) > 0:
                body_of_req = json.loads(request.data)
            else:
                body_of_req = {}

        to_edit_row = CarbonEmission.query.get(model_id)

        if to_edit_row is None:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404

        form = CarbonEmissionForm(MultiDict(body_of_req), obj=to_edit_row)
        if not form.validate():
            return {
                'message': form.errors,
                'success': False
            }, 404

        for field in body_of_req:
            setattr(to_edit_row, field, body_of_req[field])
        db.session.commit()
        return {
            'message': 'record updated',
            'success': True
        }, 200

    @token_required
    def delete(self, model_id: int):
        to_delete = CarbonEmission.query.get(model_id)
        if to_delete is None:
            return {
                'message': 'matching record not found',
                'success': False
            }, 404
        db.session.delete(to_delete)
        db.session.commit()
        return {
            'message': 'record deleted!',
            'success': True
        }, 200

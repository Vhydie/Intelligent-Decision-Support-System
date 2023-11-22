# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.models    import *
from apps.home.main_function    import *
from apps.config import API_GENERATOR
import decimal, json


@blueprint.route('/index')
@login_required
def index():
    latest_year = get_last_year_carbon_emission()
    first_year = get_first_year_carbon_emission()
    # Keperluan section pertama
    # Mengambil data tahun lalu
    amount_latest_value, energy_latest_value, cost_latest_value, carbon_latest_value = get_totals_by_year(latest_year)
    # Mengambil rate latest terhadap latest-1 
    amount_latest_1, energy_latest_1, cost_latest_1, carbon_latest_1 = get_totals_by_year(latest_year-1)
    amount_asis_rate_value = calculate_rate(amount_latest_1, amount_latest_value)
    energy_asis_rate_value = calculate_rate(energy_latest_1, energy_latest_value)
    cost_asis_rate_value = calculate_rate(cost_latest_1, cost_latest_value)
    carbon_asis_rate_value = calculate_rate(carbon_latest_1, carbon_latest_value)
    # Mengambil rate latest terhadap latest + 1
    amount_latest_pred_value, energy_latest_pred_value, cost_latest_pred_value, carbon_latest_pred_value = get_totals_by_year(latest_year+1)
    amount_pred_rate_value = calculate_rate(amount_latest_value, amount_latest_pred_value)
    energy_pred_rate_value = calculate_rate(energy_latest_value, energy_latest_pred_value)
    cost_pred_rate_value = calculate_rate(cost_latest_value, cost_latest_pred_value)
    carbon_pred_rate_value = calculate_rate(carbon_latest_value, carbon_latest_pred_value)
    # Mengirimkan ke HTML
    amount_latest = "{:,.0f}".format(amount_latest_value).replace(',', '.')
    energy_latest = "{:,.0f}".format(energy_latest_value / 1000).replace(',', '.')
    cost_latest = "{:,.2f}".format(cost_latest_value / 1000000000).replace('.', ',')
    carbon_latest = "{:,.0f}".format(carbon_latest_value / 1000).replace(',', '.')
    amount_asis_rate = "{:,.2f}".format(amount_asis_rate_value).replace('.', ',')
    energy_asis_rate = "{:,.0f}".format(energy_asis_rate_value).replace('.', ',')
    cost_asis_rate = "{:,.0f}".format(cost_asis_rate_value).replace('.', ',')
    carbon_asis_rate = "{:,.0f}".format(carbon_asis_rate_value).replace('.', ',')
    amount_latest_pred = "{:,.0f}".format(amount_latest_pred_value).replace(',', '.')
    energy_latest_pred = "{:,.0f}".format(energy_latest_pred_value / 1000).replace(',', '.')
    cost_latest_pred = "{:,.2f}".format(cost_latest_pred_value / 1000000000).replace('.', ',')
    carbon_latest_pred = "{:,.0f}".format(carbon_latest_pred_value / 1000).replace(',', '.')
    amount_pred_rate = "{:,.2f}".format(amount_pred_rate_value).replace('.', ',')
    energy_pred_rate = "{:,.0f}".format(energy_pred_rate_value).replace('.', ',')
    cost_pred_rate = "{:,.0f}".format(cost_pred_rate_value).replace('.', ',')
    carbon_pred_rate = "{:,.0f}".format(carbon_pred_rate_value).replace('.', ',')
    
    # Keperluan section kedua
    # Mengambil data untuk keperluan visualisasi bar chart
    data = []
    years = []
    predicted_rates = []
    actual_rates = []
    actual = True
    for i in range (latest_year-6,latest_year+4):
        if (i == latest_year+1):
            actual = False
        temp = []
        if (i == 0):
            amount, energy, cost, carbon = get_totals_by_year(i)
        else:
            amount, energy, cost, carbon = get_totals_by_year(i)
            amount_1, energy_1, cost_1, carbon_1 = get_totals_by_year(i-1)
            rate = calculate_rate(amount_1, amount)
            if (actual):
                actual_rates.append(rate)
            else:
                predicted_rates.append(rate)
        temp.append(amount)
        temp.append(energy)
        temp.append(cost)
        temp.append(carbon)
        data.append(temp)
        years.append(i)
    # Mengambil data untuk keperluan informasi bar chart
    total_unit_asis_value = get_total_unit()
    total_unit_asis = "{:,.1f}".format(total_unit_asis_value/1000).replace('.', ',')
    total_eol_pred = get_total_eol_unit(latest_year - 10)
    total_eol_pred = "{:,.1f}".format(total_eol_pred/1000).replace('.', ',')
    avg_actual_rate = sum(actual_rates) / len(actual_rates)
    avg_actual_rate = "{:,.1f}".format(avg_actual_rate).replace('.', ',')
    avg_pred_rate = sum(predicted_rates) / len(predicted_rates)
    avg_pred_rate = "{:,.1f}".format(avg_pred_rate).replace('.', ',')
    
    # Keperluan section ketiga
    data_asis = get_emission_category_subcategory()
    waste_by_category, total_waste = electronic_waste(data_asis, latest_year+1)
    initiatives = alternative_initiatives(amount_pred_rate_value, total_waste, total_unit_asis_value-total_waste, carbon_pred_rate_value)
    description, practices = initiative_desc(initiatives)
    units, disposed, procured = initative_action(initiatives, amount_latest_pred_value, total_waste)
    
    # Keperluan section keempat
    asset_row, loc_row, category_row, subcategory_row = get_row_count();
    asset_row = "{:,.0f}".format(asset_row).replace(',', '.')
    loc_row = "{:,.0f}".format(loc_row).replace(',', '.')
        
    return render_template('home/index.html', asset_row=asset_row, loc_row=loc_row, category_row=category_row, subcategory_row=subcategory_row, first_year=first_year, latest_year=latest_year,
                           data=data, years=years, total_unit_asis=total_unit_asis, total_eol_pred=total_eol_pred, avg_actual_rate=avg_actual_rate, avg_pred_rate=avg_pred_rate,
                           amount_latest=amount_latest, energy_latest=energy_latest, cost_latest=cost_latest, carbon_latest=carbon_latest, 
                           initiatives=initiatives, initiative_desc=description, practices=practices, units=units, disposed=disposed, procured=procured,
                           amount_latest_pred=amount_latest_pred, energy_latest_pred=energy_latest_pred, cost_latest_pred=cost_latest_pred, carbon_latest_pred=carbon_latest_pred,
                           amount_asis_rate=amount_asis_rate, energy_asis_rate=energy_asis_rate, cost_asis_rate=cost_asis_rate, carbon_asis_rate=carbon_asis_rate,
                           amount_pred_rate=amount_pred_rate, energy_pred_rate=energy_pred_rate, cost_pred_rate=cost_pred_rate, carbon_pred_rate=carbon_pred_rate,
                           segment='index', API_GENERATOR=len(API_GENERATOR))


@blueprint.route('/<template>', methods=['GET', 'POST'])
@login_required
def route_template(template):

    try:
        latest_year = get_last_year_carbon_emission()
        # Mengambil data untuk keperluan pemodelan charts
        last_15_year = latest_year - 14
        last_10_year = latest_year - 9
        last_5_year = latest_year - 4
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)
        
        if segment == "locations":
            per_page = 15
            query = Location.query.order_by(Location.kode_lokasi.desc())
            searchBy = request.form.get('searchBy')
            searchText = request.form.get('searchText')
            if searchBy and searchText:
                query = location_searching(searchBy, searchText, query)
                locations = query.order_by(Location.kode_lokasi.desc()).paginate(1, 50, error_out=False)
            else:
                page = request.args.get('page', default=1, type=int)
                locations = query.order_by(Location.kode_lokasi.desc()).paginate(page, per_page, error_out=False)                                
            location_missing_values(locations)
            return render_template('home/locations.html', locations=locations, segment=segment, API_GENERATOR=len(API_GENERATOR))
        
        elif segment == "emission_factors":
            per_page = 15
            query = EmissionFactors.query.order_by(EmissionFactors.kode_ef.desc())
            searchBy = request.form.get('searchBy')
            searchText = request.form.get('searchText')
            if searchBy and searchText:
                query = emission_factors_searching(searchBy, searchText, query)
                emission_factors = query.order_by(EmissionFactors.kode_ef.desc()).paginate(1, 50, error_out=False)
            else:
                page = request.args.get('page', default=1, type=int)
                emission_factors = query.order_by(EmissionFactors.kode_ef.desc()).paginate(page, per_page, error_out=False)
            for item in emission_factors.items:
                item.nilai_ef = "{:,.2f}".format(item.nilai_ef)
            emission_factors_missing_values(emission_factors)
            
            current_electricity_id = get_current_electricity_id()
            current_carbon_id = get_current_carbon_id()
            return render_template('home/emission_factors.html', emission_factors=emission_factors, segment=segment, API_GENERATOR=len(API_GENERATOR), current_electricity_id=current_electricity_id, current_carbon_id=current_carbon_id)

        elif segment == "asset_categories":
            per_page = 15
            query = AssetCategory.query
            searchBy = request.form.get('searchBy')
            searchText = request.form.get('searchText')
            if searchBy and searchText:
                query = asset_categories_searching(searchBy, searchText, query)
                asset_categories = query.paginate(1, 50, error_out=False)
            else:
                page = request.args.get('page', default=1, type=int)
                asset_categories = query.paginate(page, per_page, error_out=False)
            for item in asset_categories.items:
                item.asset_ef = "{:,.2f}".format(item.asset_ef)
            asset_categories_missing_values(asset_categories)
            
            # Mengambil data "major_category_name" dari tabel "asset_category"
            major_categories = AssetCategory.query.with_entities(AssetCategory.major_category_name).distinct().all()
            major_categories = [category[0] for category in major_categories]
            # Mengambil data "category_name" dari tabel "asset_category"
            categories = AssetCategory.query.with_entities(AssetCategory.category_name).distinct().all()
            categories = [category[0] for category in categories]
            
            return render_template('home/asset_category.html', asset_categories=asset_categories, segment=segment, API_GENERATOR=len(API_GENERATOR), major_categories=major_categories, categories=categories)

        elif segment == "asset_data":
            per_page = 15
            query = CarbonEmission.query.order_by(CarbonEmission.nomor_aset.desc())
            searchBy = request.form.get('searchBy')
            searchText = request.form.get('searchText')
            if searchBy and searchText:
                query = asset_data_searching(searchBy, searchText, query)
                asset_data = query.order_by(CarbonEmission.nomor_aset.desc()).paginate(1, 50, error_out=False)
            else:
                page = request.args.get('page', default=1, type=int)
                asset_data = query.order_by(CarbonEmission.nomor_aset.desc()).paginate(page, per_page, error_out=False)
            for item in asset_data.items:
                item.cost = "{:,.2f}".format(item.cost)
                item.energy = "{:,.2f}".format(item.energy)
                item.carbon = "{:,.2f}".format(item.carbon)
            asset_data_missing_values(asset_data)
            # Mengambil data "category_code" dari tabel "asset_category"
            category_data = AssetCategory.query.with_entities(AssetCategory.kode_kategori, AssetCategory.sub_category_name).distinct().all()
            category_code = [category[0] for category in category_data]
            sub_category = [category[1] for category in category_data]
            combined_options = [f"{category_code} - {sub_category}" for category_code, sub_category in zip(category_code, sub_category)]
            # Mengambil data "location_code" dari tabel "asset_category"
            location_code = Location.query.with_entities(Location.kode_lokasi).distinct().all()
            location_code = [location[0] for location in location_code]
            return render_template('home/asset_data.html', asset_data=asset_data, segment=segment, API_GENERATOR=len(API_GENERATOR), combined_options=combined_options, location_code=location_code)
        
        elif segment == "emissions":
            data = formatted_data(get_emission_subcategory())
            category_data = formatted_data(get_emission_category())
            searchBy = request.form.get('searchBy')
            searchText = request.form.get('searchText')
            if searchBy and searchText:
                ## Mengetahui apa yang difokuskan untuk dicari
                if searchBy == 'category_name':
                    category_query = emission_searching(searchBy, searchText, category_data)
                    emissions = paginate_data(data, 1, 36)
                    category_emissions = paginate_data(category_query, 1, 20)
                elif searchBy == 'sub_category_name':
                    query = emission_searching(searchBy, searchText, data)
                    emissions = paginate_data(query, 1, 20)
                    category_emissions = paginate_data(category_data, 1, 6)
                else:
                    query = emission_searching(searchBy, searchText, data)
                    category_query = emission_searching(searchBy, searchText, category_data)
                    emissions = paginate_data(query, 1, 50)
                    category_emissions = paginate_data(category_query, 1, 10)
            else:
                page = request.args.get('page', default=1, type=int)
                emissions = paginate_data(data, page, 36)
                page = request.args.get('page', default=1, type=int)
                category_emissions = paginate_data(category_data, page, 6)
            return render_template('home/emissions.html', emissions=emissions, category_emissions=category_emissions, segment=segment, API_GENERATOR=len(API_GENERATOR))

        elif segment == "carbon_calculation":
            asset_categories = AssetCategory.query.with_entities(AssetCategory.category_name).distinct().all()
            return render_template('home/carbon_calculation.html', asset_categories=asset_categories, segment=segment, API_GENERATOR=len(API_GENERATOR))
        
        elif segment == "asset_ef_calculation":
            asset_categories = AssetCategory.query.with_entities(AssetCategory.category_name).distinct().all()
            return render_template('home/asset_ef_calculation.html', asset_categories=asset_categories, segment=segment, API_GENERATOR=len(API_GENERATOR))
        
        elif segment == "model_units_view":
            # Mengambil data untuk keperluan pemodelan charts untuk asset categories
            total_unit_by_category_last_15_years = get_year_subcategory_unit(last_15_year)
            # Mengambil data "category_name" dari tabel "asset_category"
            categories = AssetCategory.query.with_entities(AssetCategory.category_name).distinct().all()
            categories = [category[0] for category in categories]
            return render_template('home/model_units_view.html', categories=categories,last_15_year=last_15_year, last_10_year=last_10_year, last_5_year=last_5_year, 
                                   latest_year=latest_year,total_unit_by_category_last_15_years=total_unit_by_category_last_15_years,
                                   segment=segment, API_GENERATOR=len(API_GENERATOR))
        
        elif segment == "model_asset_calculation":
            # Mengambil data "category_name" dari tabel "asset_category"
            categories = AssetCategory.query.with_entities(AssetCategory.category_name).distinct().all()
            categories = [category[0] for category in categories]
            emission_data = get_emission_over_year(get_emission_category_subcategory(), last_15_year)
            return render_template('home/model_asset_calculation.html', last_15_year=last_15_year, last_10_year=last_10_year, last_5_year=last_5_year, latest_year=latest_year,
                                   categories=categories, get_emission_over_year=emission_data, segment=segment, API_GENERATOR=len(API_GENERATOR))
        
        elif segment == "predictions":
            # Mengirimkan pilihan categories
            asset_categories = AssetCategory.query.with_entities(AssetCategory.category_name).distinct().all()
            asset_categories_length = len(asset_categories)
            return render_template("home/predictions.html", asset_categories=asset_categories, asset_categories_length=asset_categories_length, latest_year=latest_year, segment=segment, API_GENERATOR=len(API_GENERATOR))
        
        else:
            return render_template("home/" + template, segment=segment, API_GENERATOR=len(API_GENERATOR))

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

    
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None
    
    
@blueprint.route('/sub_category/<category_name>')
@login_required
def get_subcategories(category_name):
    sub_categories = AssetCategory.query.with_entities(AssetCategory.sub_category_name).filter_by(category_name=category_name).distinct().all()
    sub_category_names = [row[0] for row in sub_categories]
    return {'sub_categories': sub_category_names}

@blueprint.route('/get_ef_aset', methods=['GET'])
@login_required
def get_ef_aset():
    category = request.args.get('category')
    sub_category = request.args.get('sub_category')
    
    asset = AssetCategory.query.filter_by(category_name=category, sub_category_name=sub_category).first()
    
    if asset:
        return str(asset.asset_ef)
    
    return ''

@blueprint.route('/calculate', methods=['POST'])
@login_required
def calculate_totals():
    data = request.get_json()

    # Ambil nilai total_energy dari data JSON yang diterima
    energy = data.get('total_energy', 0)
    sub_category = data.get('sub_category')

    efel_records = EmissionFactors.query.filter(EmissionFactors.kode_ef.like("EFEL%")).order_by(EmissionFactors.tahun_relevansi_ef.desc()).all()
    efce_records = EmissionFactors.query.filter(EmissionFactors.kode_ef.like("EFCE%")).order_by(EmissionFactors.tahun_relevansi_ef.desc()).all()

    cost = 0
    emission = 0

    if efel_records:
        highest_efel_value = efel_records[0].nilai_ef
        cost = energy * highest_efel_value

    if efce_records:
        highest_efce_value = efce_records[0].nilai_ef
        emission = energy * highest_efce_value

    response = {
        'cost': cost,
        'emission': emission
    }
    # Menghitung total_emission_subcategory dari seluruh tahun
    total_emission = db.session.query(
        func.sum(CarbonEmission.carbon).label('total_carbon')
    ).join(
        AssetCategory, CarbonEmission.kode_kategori == AssetCategory.kode_kategori
    ).filter(
        AssetCategory.sub_category_name == sub_category
    ).scalar()
    # Lakukan perhitungan total_emission_subcategory di sini

    response['total_emission'] = total_emission

    return jsonify(response)

@blueprint.route('/predict_operations', methods=['POST'])
@login_required
def predict_emissions():
    data = request.get_json()
    # Dapatkan nilai category, subcategory, dan yearsToPredict dari data
    category = data.get('category')
    subcategory = data.get('subcategory')
    years_to_predict = data.get('yearsToPredict')
    if (years_to_predict == "1 Years from the Latest Years"):
        years_to_predict = 1
    elif (years_to_predict == "2 Years from the Latest Years"):
        years_to_predict = 2
    elif (years_to_predict == "3 Years from the Latest Years"):
        years_to_predict = 3
    elif (years_to_predict == "4 Years from the Latest Years"):
        years_to_predict = 4
    elif (years_to_predict == "5 Years from the Latest Years"):
        years_to_predict = 5
        
    # Konversi data menjadi dataframe
    actual = get_emission_category_subcategory()
    df = convert_to_dataframe(actual)
    if category:
        df = slice_by_category(df, category)
    elif subcategory:
        df = slice_by_subcategory(df, subcategory)

    # Menghitung waste
    latest_year = get_last_year_carbon_emission()
    waste_by_category, total_waste = electronic_waste(df.values, latest_year + years_to_predict)
    # Menghapus outliers
    df_clean = replace_outliers_with_upper_bound(df, detect_outliers(df))
    # Transformasi menjadi time-series format data frame
    df_model = transform_dataframe(df_clean)
    # Modelling
    years_to_train = 5
    train, subcategories, test = trained_data(df_model, years_to_train, 3)
    # Modelling
    model_orders = (1, 1, 2)
    
    predictions = modelling(train, test, years_to_predict, model_orders, subcategories)
    prediction_overview = calculate_emissions_from_predicted_per_year(predictions, subcategories, latest_year, years_to_predict)
    prediction_total_units = calculate_column_totals(predictions)
    result = calculate_actual_and_prediction_emissions(actual, prediction_overview, (latest_year + years_to_predict - 10))

    # Initiatives
    df_result = result
    if category:
        df_result = filter_data_by_category(result, category)
    elif subcategory:
        df_result = filter_data_by_subcategory(result, subcategory)    
        
    if (len(prediction_total_units) >= 2):
        total_prediction = sum(prediction_total_units[:-1])
        last_pred = prediction_total_units[-2]
    else: 
        total_prediction = 0
        last_pred = 0
    
    total_unit = get_total_unit() + total_prediction
    amount_latest_pred_value = prediction_total_units[-1]
    amount_pred_rate_value = calculate_rate(last_pred, amount_latest_pred_value)
    
    carbon_pred_rate_value = (predictions_group_by_year(df_result))[-1][-1]
    initiatives = alternative_initiatives(amount_pred_rate_value, total_waste, total_unit-total_waste, carbon_pred_rate_value)
    description, practices = initiative_desc(initiatives)
    units, disposed, procured = initative_action(initiatives, amount_latest_pred_value, total_waste)
    
    # Mengembalikan hasil sebagai respons JSON
    response = {
        'years_to_predict': years_to_predict,
        'actual': actual,
        'predictions': predictions,
        'predictions_total_unit': prediction_total_units,
        'prediction_overview': prediction_overview,
        'result': result,
        'initiatives': initiatives,
        'description': description,
        'practices': practices,
        'units': units,
        'disposed': disposed,
        'procured': procured
    }
    return jsonify(response)



# CRUD LOCATIONS DATA
# CRUD LOCATIONS DATA
# CRUD LOCATIONS DATA
@blueprint.route('/add_location', methods=['POST'])
@login_required
def add_location():
    location_code = request.form.get('location_code')
    building_name = request.form.get('building_name')
    room_name = request.form.get('room_name')

    new_location = Location(location_code=location_code, building_name=building_name, room_name=room_name)

    try:
        db.session.add(new_location)
        db.session.commit()
        additon_status = 'success'
    except Exception as e:
        db.session.rollback()
        additon_status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='locations', additon_status=additon_status))

@blueprint.route('/update_location/<location_id>', methods=['POST'])
@login_required
def update_location(location_id):
    location = Location.query.get(location_id)
    building_name = request.form.get('building_name')
    room_name = request.form.get('room_name')
    
    if location:
        try:
            location.nama_gedung = building_name
            location.nama_ruang = room_name
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='locations', status=status))

@blueprint.route('/delete_location/<location_id>', methods=['POST'])
@login_required
def delete_location(location_id):
    location = Location.query.get(location_id)

    if location:
        try:
            db.session.delete(location)
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='locations', status=status))


# CRUD EMISSION FACTORS DATA
# CRUD EMISSION FACTORS DATA
# CRUD EMISSION FACTORS DATA
@blueprint.route('/add_emission_factor', methods=['POST'])
@login_required
def add_emission_factor():
    emission_type = request.form.get('ef_code_type')
    emission_name = request.form.get('ef_name')
    emission_value = request.form.get('ef_value')
    relevance_year = request.form.get('ef_year')
    if emission_type == "EL_conv":
        emission_code = get_current_electricity_id()
    elif emission_type == "carbon_conv":
        emission_code = get_current_carbon_id()
    new_emission_factor = EmissionFactors(kode_ef=emission_code, nama_ef=emission_name, nilai_ef=emission_value, tahun_relevansi_ef=relevance_year)

    try:
        db.session.add(new_emission_factor)
        db.session.commit()
        addition_status = 'success'
    except Exception as e:
        db.session.rollback()
        addition_status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='emission_factors', addition_status=addition_status))

@blueprint.route('/update_emission_factor/<ef_id>', methods=['POST'])
@login_required
def update_emission_factor(ef_id):
    emission_factor = EmissionFactors.query.get(ef_id)
    emission_name = request.form.get('ef_name')
    emission_value = request.form.get('ef_value')
    relevance_year = request.form.get('ef_year')

    if emission_factor:
        try:
            emission_factor.nama_ef = emission_name
            emission_factor.nilai_ef = emission_value
            emission_factor.tahun_relevansi_ef = relevance_year
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='emission_factors', status=status))

@blueprint.route('/delete_emission_factor/<ef_id>', methods=['POST'])
@login_required
def delete_emission_factor(ef_id):
    emission_factor = EmissionFactors.query.get(ef_id)

    if emission_factor:
        try:
            db.session.delete(emission_factor)
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='emission_factors', status=status))


# CRUD ASSET CATEGORY DATA
# CRUD ASSET CATEGORY DATA
# CRUD ASSET CATEGORY DATA
@blueprint.route('/add_asset_category', methods=['POST'])
@login_required
def add_asset_category():
    major_category_name = request.form.get('major_category_name')
    category_name = request.form.get('category_name')
    sub_category_name = request.form.get('sub_category')
    asset_ef = request.form.get('asset_ef')
    
    # Generating asset category code
    major_category = get_major_category_from_major_category_name(major_category_name)
    category = get_category_from_category_name(category_name)
    sub_category = get_sub_category_from_category(category)

    category_code = f"{major_category}.{category}.{sub_category}"
    new_asset_category = AssetCategory(
        kode_kategori=category_code,
        major_category=major_category,
        major_category_name=major_category_name,
        category=category,
        category_name=category_name,
        sub_category=sub_category,
        sub_category_name=sub_category_name,
        asset_ef=asset_ef
    )
    
    try:
        db.session.add(new_asset_category)
        db.session.commit()
        addition_status = 'success'
    except Exception as e:
        db.session.rollback()
        addition_status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='asset_categories', addition_status=addition_status))

@blueprint.route('/update_asset_category/<kategori_id>', methods=['POST'])
@login_required
def update_asset_category(kategori_id):
    asset_category = AssetCategory.query.get(kategori_id)
    sub_category_name = request.form.get('sub_category_name_edit')
    asset_ef = request.form.get('asset_ef_edit')

    if asset_category:
        try:
            asset_category.sub_category_name = sub_category_name
            asset_category.asset_ef = asset_ef
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='asset_categories', status=status))

@blueprint.route('/delete_asset_category/<kategori_id>', methods=['POST'])
@login_required
def delete_asset_category(kategori_id):
    asset_category = AssetCategory.query.get(kategori_id)

    if asset_category:
        try:
            db.session.delete(asset_category)
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='asset_categories', status=status))


# CRUD ASSET DATA
# CRUD ASSET DATA
# CRUD ASSET DATA
@blueprint.route('/add_asset_data', methods=['POST'])
@login_required
def add_asset_data():
    nomor_aset = request.form.get('asset_number')
    kode_lokasi = request.form.get('location_code')
    unit_kerja = request.form.get('work_unit')
    kelompok_kode_kategori = request.form.get('category_code')
    kode_kategori, sub_kategori = kelompok_kode_kategori.split(" - ", 1)
    deskripsi = request.form.get('desc')
    tahun_perolehan = int(request.form.get('year'))
    jumlah_unit = int(request.form.get('amount'))
    
    new_asset_data = CarbonEmission(
        nomor_aset=nomor_aset,
        kode_lokasi=kode_lokasi,
        unit_kerja=unit_kerja,
        kode_kategori=kode_kategori,
        deskripsi=deskripsi,
        tahun_perolehan=tahun_perolehan,
        jumlah_unit=jumlah_unit
    )

    try:
        db.session.add(new_asset_data)
        db.session.commit()
        status = 'success'
    except Exception as e:
        db.session.rollback()
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='asset_data', status=status))

@blueprint.route('/update_asset_data/<aset_id>', methods=['POST'])
@login_required
def update_asset_data(aset_id):
    asset_data = CarbonEmission.query.get(aset_id)
    if asset_data:
        kelompok_kode_kategori = request.form.get('category_code_input')
        if "-" in kelompok_kode_kategori:
            kode_kategori, sub_kategori = kelompok_kode_kategori.split(" - ", 1)
        else:
            kode_kategori = kelompok_kode_kategori.replace(" ", "")
            
        amount = int(request.form.get('jumlah_unit_edit'))
        ef_aset = (AssetCategory.query.filter_by(kode_kategori=kode_kategori).first()).asset_ef
        ef_electricity = (EmissionFactors.query.filter(EmissionFactors.kode_ef.like("EFEL%")).order_by(EmissionFactors.tahun_relevansi_ef.desc()).first()).nilai_ef
        ef_carbon = (EmissionFactors.query.filter(EmissionFactors.kode_ef.like("EFCE%")).order_by(EmissionFactors.tahun_relevansi_ef.desc()).first()).nilai_ef

        energy = amount * ef_aset
        cost = energy * ef_electricity
        carbon = energy * ef_carbon
        
        asset_data.kode_lokasi = request.form.get('location_code_input')
        asset_data.unit_kerja = request.form.get('unit_kerja_edit')
        asset_data.kode_kategori = kode_kategori
        asset_data.deskripsi = request.form.get('deskripsi_edit')
        asset_data.tahun_perolehan = int(request.form.get('tahun_perolehan_edit'))
        asset_data.jumlah_unit = amount
        asset_data.energy = decimal.Decimal(energy or '0.00000')
        asset_data.cost = decimal.Decimal(cost or '0.00000')
        asset_data.carbon = decimal.Decimal(carbon or '0.00000')
        

        try:
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='asset_data', status=status))

@blueprint.route('/delete_asset_data/<int:aset_id>', methods=['POST'])
@login_required
def delete_asset_data(aset_id):
    asset_data = CarbonEmission.query.get(aset_id)

    if asset_data:
        try:
            db.session.delete(asset_data)
            db.session.commit()
            status = 'success'
        except Exception as e:
            db.session.rollback()
            status = 'error'
    else:
        status = 'error'

    return redirect(url_for('home_blueprint.route_template', template='asset_data', status=status))

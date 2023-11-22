# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps import db
from sqlalchemy.sql import func, distinct
from statsmodels.tsa.arima.model import ARIMA
from operator import itemgetter
import math, locale, decimal
import pandas as pd
import numpy as np


# Data from database
# Data from database
# Data from database
# Location Class
class Location(db.Model):
    __tablename__ = 'location' 
    kode_lokasi = db.Column(db.String(50), primary_key=True)
    nama_gedung = db.Column(db.String(100), nullable=False)
    nama_ruang = db.Column(db.String(100), nullable=False)
    
    def __init__(self, location_code, building_name, room_name):
        self.kode_lokasi = location_code
        self.nama_gedung = building_name
        self.nama_ruang = room_name

# Asset Category Class
class AssetCategory(db.Model):
    __tablename__ = 'asset_category'  
    kode_kategori = db.Column(db.String(40), primary_key=True)
    major_category = db.Column(db.String(10), nullable=False)
    major_category_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(10), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    sub_category = db.Column(db.String(10), nullable=False)
    sub_category_name = db.Column(db.String(100), nullable=False)
    asset_ef = db.Column(db.Float, nullable=False, default=0)

# Emission Factors Class
class EmissionFactors(db.Model):
    __tablename__ = 'emission_factors'  
    kode_ef = db.Column(db.String(10), primary_key=True)
    nama_ef = db.Column(db.String(100), nullable=False)
    nilai_ef = db.Column(db.Float, nullable=False, default=0)
    tahun_relevansi_ef = db.Column(db.Integer, nullable=False)

# Asset Data Class
class CarbonEmission(db.Model):
    __tablename__ = 'carbon_emission'
    id_aset = db.Column(db.Integer, primary_key=True)
    nomor_aset = db.Column(db.String(50))
    kode_lokasi = db.Column(db.String(50))
    unit_kerja = db.Column(db.String(50))
    kode_kategori = db.Column(db.String(50))
    deskripsi = db.Column(db.String(255))
    tahun_perolehan = db.Column(db.Integer)
    jumlah_unit = db.Column(db.Integer, default=1)
    energy = db.Column(db.Numeric(20, 5), default=0.00000)
    cost = db.Column(db.Numeric(20, 5), default=0.00000)
    carbon = db.Column(db.Numeric(20, 5), default=0.00000)

# Temp Data Class untuk Actual + Predicted
class TempData(db.Model):
    __tablename__ = 'temp_data'
    temp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    energy = db.Column(db.Numeric(20, 5))
    cost = db.Column(db.Numeric(20, 5))
    carbon = db.Column(db.Numeric(20, 5))


# Data Acess & Modification Function
# Data Acess & Modification Function
# Data Acess & Modification Function
# Function untuk mengubah format data menjadi ribuan
def format_thousands(number):
    return "{:,}".format(number)

# Function untuk mengambil tahun perolehan terakhir
def get_last_year_carbon_emission():
    lastest_year = db.session.query(func.max(CarbonEmission.tahun_perolehan)).scalar()
    return lastest_year

# Function untuk mengambil tahun perolehan terakhir
def get_first_year_carbon_emission():
    first_year = db.session.query(func.min(CarbonEmission.tahun_perolehan)).scalar()
    return first_year

# Function untuk formatting data cost, energy, dan carbon
def formatted_data(data):
    # Set locale to Indonesian
    locale.setlocale(locale.LC_ALL, 'id_ID')
    for i, row in enumerate(data):
        # Format cost, energy, and carbon
        energy = locale.format('%.2f', float(row[3]), grouping=True)
        cost = locale.format('%.2f', float(row[4]), grouping=True)
        carbon = locale.format('%.2f', float(row[5]), grouping=True)
        data[i] = (*row[:3], energy, cost, carbon)
    locale.setlocale(locale.LC_ALL, '')
    return data

# Function untuk pgnation
def paginate_data(data, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = data[start:end]
    total_items = len(data)
    total_pages = math.ceil(total_items / per_page)

    class Pagination:
        def __init__(self, items, page, per_page, total_items, total_pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total_items = total_items
            self.total_pages = total_pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < total_pages else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
            last = 0
            for num in range(1, self.total_pages + 1):
                if (
                    num <= left_edge
                    or (
                        num > self.page - left_current - 1
                        and num < self.page + right_current
                    )
                    or num > self.total_pages - right_edge
                ):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    paginated_data = Pagination(paginated_data, page, per_page, total_items, total_pages)
    return paginated_data



# Dataset Creation Function
# Dataset Creation Function
# Dataset Creation Function
# Function untuk mendapatkan keseluruhan data (jumlah unit, energy, cost, carbon) per tahun per subcategory per masing-masing data point
def get_emission_subcategory():
    results = db.session.query(
        CarbonEmission.tahun_perolehan,
        CarbonEmission.kode_kategori,
        func.sum(CarbonEmission.jumlah_unit).label('total_unit'),
        func.sum(CarbonEmission.energy).label('total_energy'),
        func.sum(CarbonEmission.cost).label('total_cost'),
        func.sum(CarbonEmission.carbon).label('total_carbon')
    ).group_by(
        CarbonEmission.tahun_perolehan,
        CarbonEmission.kode_kategori
    ).order_by(
        CarbonEmission.tahun_perolehan,
        CarbonEmission.kode_kategori
    ).all()

    # Iterate over the results and handle missing combinations
    data = []
    years = set()
    categories = set()

    for row in results:
        years.add(row.tahun_perolehan)
        categories.add(row.kode_kategori)

    for year in years:
        for category in categories:
            found = False
            for row in results:
                if row.tahun_perolehan == year and row.kode_kategori == category:
                    found = True
                    data.append(row)
                    break
            if not found:
                data.append((year, category, 0, 0.00000, 0.00000, 0.00000))
    for i, row in enumerate(data):
        year = row[0]
        category = row[1]
        sub_category_name = db.session.query(AssetCategory.sub_category_name).filter_by(kode_kategori=category).first()
        sub_category_name = sub_category_name[0] if sub_category_name else None
        data[i] = (*row[:1], sub_category_name, *row[2:])
    data_sorted = sorted(data, key=lambda x: (x[0], x[1]))
    return data_sorted

# Function untuk mendapatkan keseluruhan data (jumlah unit, energy, cost, carbon) per tahun per category per masing-masing data point
def get_emission_category():
    years = db.session.query(distinct(CarbonEmission.tahun_perolehan)).all()
    categories = db.session.query(distinct(AssetCategory.category_name)).all()

    results = db.session.query(
        CarbonEmission.tahun_perolehan,
        AssetCategory.category_name,
        func.coalesce(func.sum(CarbonEmission.jumlah_unit), 0),
        func.coalesce(func.sum(CarbonEmission.energy), 0),
        func.coalesce(func.sum(CarbonEmission.cost), 0),
        func.coalesce(func.sum(CarbonEmission.carbon), 0)
    ).outerjoin(
        AssetCategory,
        CarbonEmission.kode_kategori == AssetCategory.kode_kategori
    ).filter(
        CarbonEmission.tahun_perolehan.in_([year[0] for year in years]),
        AssetCategory.category_name.in_([category[0] for category in categories])
    ).group_by(
        CarbonEmission.tahun_perolehan,
        AssetCategory.category_name
    ).order_by(
        CarbonEmission.tahun_perolehan,
        AssetCategory.category_name
    ).all()

    emissions_list = []
    for year in years:
        for category in categories:
            found = False
            for row in results:
                if row.tahun_perolehan == year[0] and row.category_name == category[0]:
                    emissions_list.append(list(row))
                    found = True
                    break
            if not found:
                emissions_list.append([year[0], category[0], 0, 0, 0, 0])
    data_sorted = sorted(emissions_list, key=lambda x: (x[0], x[1]))
    return data_sorted

# Function untuk mendapatkan keseluruhan data (jumlah unit, energy, cost, carbon) per tahun per (category & subcategory) per masing-masing data point. Data digunakan untuk pemodelan model prediksi.
def get_emission_category_subcategory():
    results = db.session.query(
        CarbonEmission.tahun_perolehan,
        CarbonEmission.kode_kategori,
        func.sum(CarbonEmission.jumlah_unit).label('total_unit'),
        func.sum(CarbonEmission.energy).label('total_energy'),
        func.sum(CarbonEmission.cost).label('total_cost'),
        func.sum(CarbonEmission.carbon).label('total_carbon')
    ).group_by(
        CarbonEmission.tahun_perolehan,
        CarbonEmission.kode_kategori
    ).order_by(
        CarbonEmission.tahun_perolehan,
        CarbonEmission.kode_kategori
    ).all()

    # Iterate over the results and handle missing combinations
    data = []
    years = set()
    categories = set()

    for row in results:
        years.add(row.tahun_perolehan)
        categories.add(row.kode_kategori)

    for year in years:
        for category in categories:
            found = False
            for row in results:
                if row.tahun_perolehan == year and row.kode_kategori == category:
                    found = True
                    data.append(row)
                    break
            if not found:
                data.append((year, category, 0, 0.00000, 0.00000, 0.00000))
    for i, row in enumerate(data):
        year = row[0]
        category = row[1]
        sub_category_name = db.session.query(AssetCategory.sub_category_name).filter_by(kode_kategori=category).first()
        sub_category_name = sub_category_name[0] if sub_category_name else None
        category_name = db.session.query(AssetCategory.category_name).filter_by(kode_kategori=category).first()
        category_name = category_name[0] if category_name else None
        data[i] = (*row[:1], category_name, sub_category_name, *row[2:])
    data_sorted = sorted(data, key=lambda x: (x[0], x[1]))
    return data_sorted

# Function untuk mengambil data emisi yang merupakan akumulasi per tahun, bukan data point, untuk batasan tahun tertentu. Data yang digunakan untuk pemodelan emisi.
def get_emission_over_year(data, year):
    # Mengelompokkan data berdasarkan tahun_perolehan
    grouped_data = {}
    for item in data:
        tahun_perolehan = item[2]
        if tahun_perolehan not in grouped_data:
            grouped_data[tahun_perolehan] = []
        grouped_data[tahun_perolehan].append(item)

    # Menghitung akumulasi energy, cost, dan carbon berdasarkan tahun_perolehan
    result = []
    for tahun_perolehan, items in grouped_data.items():
        items.sort(key=itemgetter(0))  # Urutkan berdasarkan tahun untuk memastikan urutan yang benar
        cumulative_energy = 0
        cumulative_cost = 0
        cumulative_carbon = 0
        for item in items:
            cumulative_energy += decimal.Decimal(item[4])
            cumulative_cost += decimal.Decimal(item[5])
            cumulative_carbon += decimal.Decimal(item[6])
            if item[0] >= year:
                result.append([
                    item[0],
                    item[1],
                    item[2],
                    cumulative_energy,
                    cumulative_cost,
                    cumulative_carbon,
                    item[3],
                ])

    result.sort(key=itemgetter(0))  # Urutkan berdasarkan tahun
    return result

# Functoin untuk hanya mengambil data jumlah_unit per category dan sub_category untuk batasan tahun tertentu. Data yang digunakan untuk pemodelan jumlah unit.
def get_year_subcategory_unit(year):
    results = get_emission_category_subcategory()
    year_subcategory_unit = []
    for result in results:
        year_perolehan = result[0]
        category = result[1]
        sub_category_name = result[2]
        jumlah_unit = int(result[3])
        if year_perolehan >= year:
            year_subcategory_unit.append((year_perolehan, category, sub_category_name, jumlah_unit))
    sorted_year_subcategory_unit = sorted(year_subcategory_unit, key=lambda x: x[1])
    return sorted_year_subcategory_unit



# Data Cleaning untuk Modelling
# Data Cleaning untuk Modelling
# Data Cleaning untuk Modelling
# Function convert to dataframe
def convert_to_dataframe(data):
    columns = ['Tahun Perolehan', 'Category', 'Subcategory', 'Jumlah Unit', 'Total Energy', 'Total Cost', 'Total Carbon']
    df = pd.DataFrame(data, columns=columns)
    df['Jumlah Unit'] = df['Jumlah Unit'].astype(int)
    df['Total Energy'] = df['Total Energy'].astype(float)
    df['Total Cost'] = df['Total Cost'].astype(float)
    df['Total Carbon'] = df['Total Carbon'].astype(float)
    return df

# Function untuk detecting outliers
def detect_outliers(df):
    # Group the data by category
    grouped = df.groupby('Category')
    # Define a list to store the outliers
    all_outliers = []

    # Iterate over each group
    for category, group in grouped:
        # Defining the Quartile for each group
        Q1 = group['Jumlah Unit'].quantile(0.25)
        Q3 = group['Jumlah Unit'].quantile(0.75)
        IQR = Q3 - Q1
        # Define the threshold for outlier detection (e.g., Q3 + 1.5 * IQR or Q1 - 1.5 * IQR)
        bts_atas = Q3 + 1.5 * IQR
        bts_bwh = Q1 - 1.5 * IQR
        # Find outliers for the current group
        outliers = group[(group['Jumlah Unit'] < bts_bwh) | (group['Jumlah Unit'] > bts_atas)][['Tahun Perolehan', 'Category', 'Subcategory', 'Jumlah Unit']]
        # Add 'Batas Atas' and 'Batas Bawah' columns to outliers DataFrame
        outliers['Batas Atas'] = bts_atas
        outliers['Batas Bawah'] = bts_bwh
        # Append the outliers to the list
        all_outliers.append(outliers)

    # Concatenate all outliers into a single DataFrame
    all_outliers = pd.concat(all_outliers)

    return all_outliers

# Function untuk slicing per category
def slice_by_category(df, category):
    sliced_df = df.loc[df['Category'] == category]
    return sliced_df

# Function untuk slicing per subcategory
def slice_by_subcategory(df, subcategory):
    sliced_df = df.loc[df['Subcategory'] == subcategory]
    return sliced_df

# Function untuk handling outliers
def replace_outliers_with_upper_bound(df, outliers):
    for _, row in outliers.iterrows():
        # Hasil eksperimen menunjukkan bahwa audio visual tidak bisa dihapus outliersnya karena rata-rata memiliki nilai 0
        category = row['Category']
        if category != 'Audio Visual':
            bts_atas = row['Batas Atas']
            df.loc[(df['Category'] == category) & (df['Jumlah Unit'] > bts_atas), 'Jumlah Unit'] = round(bts_atas)
    return df

# Function untuk mengubah format df agar bisa dimodelkan
def transform_dataframe(df):
    df_clean_v2 = df.groupby(['Subcategory', 'Tahun Perolehan'])['Jumlah Unit'].sum()
    df_clean_v2 = df_clean_v2.unstack('Tahun Perolehan').fillna(0).astype(int)
    df_clean_v2 = df_clean_v2[df_clean_v2.columns.sort_values()]
    return df_clean_v2

# Train test split dari df
def trained_data(df, year_before, n_test):
    subcategories = df.index.tolist()
    values = df.values
    train, test = values[:, :-n_test], values[:, -n_test:]
    train = train[:, -year_before:]
    return train, subcategories, test

# Function untuk pembuatan model per masing-masing category
def modelling(train, test, year_predict, order, subcategories):
    list_predictions = list()
    for k in range(len(train)):
        predictions = list()
        history = [x for x in train[k]]
        # print(f"Prediction Asset Subcategory: {subcategories[k]}")
        # print(history)
        for i in range(0, (len(test[k]) + year_predict)):
            model = ARIMA(history, order=order)
            model_fit = model.fit()
            output = model_fit.forecast()
            y_pred = output[0]
            if (y_pred < 0):
                y_pred = 0
                
            if (i < len(test[k])):
                y_act = test[k][i]
            else:
                y_act = y_pred
                predictions.append(round(y_pred))
            history.append(y_act)
            # print('predicted=%f' % (round(y_pred)))
        list_predictions.append(predictions)
    return list_predictions

# Function untuk menghitung total hasil prediksi
def calculate_column_totals(data):
    column_totals = []
    for column in zip(*data):
        total = sum(column)
        column_totals.append(total)
    return column_totals

# Function untuk mengambil ef aset berdasarkan sub_category_name
def get_asset_ef_by_sub_category(sub_category_name):
    asset_category = AssetCategory.query.filter_by(sub_category_name=sub_category_name).first()
    if asset_category:
        return asset_category.asset_ef, asset_category.category_name
    else:
        return None

# Function untuk menghitung konsumsi energy, cost, dan emisi dari predicted units
def calculate_emissions_from_predicted_per_year(predictions, subcategories, start_year, years_to_predict):
    efel_records = EmissionFactors.query.filter(EmissionFactors.kode_ef.like("EFEL%")).order_by(EmissionFactors.tahun_relevansi_ef.desc()).all()
    efce_records = EmissionFactors.query.filter(EmissionFactors.kode_ef.like("EFCE%")).order_by(EmissionFactors.tahun_relevansi_ef.desc()).all()
    energy, cost, carbon = 0, 0, 0
    calculations = list()
    for prediction, subcategory in zip(predictions, subcategories):
        ef_aset, category = get_asset_ef_by_sub_category(subcategory)
        year = start_year
        for i in range (years_to_predict):
            year += 1
            energy = ef_aset * prediction[i]
            if efel_records:
                highest_efel_value = efel_records[0].nilai_ef
                cost = energy * highest_efel_value
            if efce_records:
                highest_efce_value = efce_records[0].nilai_ef
                carbon = energy * highest_efce_value
            formatted_prediction = (decimal.Decimal(prediction[i])).quantize(decimal.Decimal("0.00000"))
            formatted_energy = (decimal.Decimal(energy)).quantize(decimal.Decimal("0.00000"))
            formatted_cost = (decimal.Decimal(cost)).quantize(decimal.Decimal("0.00000"))
            formatted_carbon = (decimal.Decimal(carbon)).quantize(decimal.Decimal("0.00000"))
            calculations.append((year, category, subcategory, formatted_prediction, formatted_energy, formatted_cost, formatted_carbon))
    return(calculations)

# Function untuk combine data dan mendapatkan total emisinya
def calculate_actual_and_prediction_emissions(actual, prediction, year):  
    data = actual + prediction
    result = get_emission_over_year(data, year)
    return result

# Function untuk jalankan prediksi sekali beserta data aktualnya
def predict():
    # Konversi data menjadi dataframe
    df = convert_to_dataframe(get_emission_category_subcategory())
    # Menghapus outliers
    df_clean = replace_outliers_with_upper_bound(df, detect_outliers(df))
    # Transformasi menjadi time-series format data frame
    df_model = transform_dataframe(df_clean)
    # Modelling
    years_to_train = 5
    train, subcategories, test = trained_data(df_model, years_to_train, 3)
    # Modelling
    model_orders = (1, 1, 2)
    years_to_predict = 3
    start_year = get_last_year_carbon_emission()
    predictions = modelling(train, test, years_to_predict, model_orders, subcategories)
    prediction_overview = calculate_emissions_from_predicted_per_year(predictions, subcategories, start_year, years_to_predict)
    actual = get_emission_category_subcategory()
    result = calculate_actual_and_prediction_emissions(actual, prediction_overview, (start_year + years_to_predict - 10))
    return result

# Function untuk menambahkan ke data temp
def insert_data_to_temp_data(data, database):
    # Menghapus semua data dari tabel TempData
    database.query.delete()

    # Memasukkan data baru ke tabel TempData
    for entry in data:
        year = entry[0]
        category = entry[1]
        subcategory = entry[2]
        amount = entry[6]
        energy = entry[3]
        cost = entry[4]
        carbon = entry[5]

        new_entry = database(
            year=year,
            category=category,
            subcategory=subcategory,
            amount=amount,
            energy=energy,
            cost=cost,
            carbon=carbon
        )
        db.session.add(new_entry)

    # Melakukan commit perubahan ke basis data
    db.session.commit()

# Function untuk mendapatkan total unit, energy, cost, dan carbon per masukan tahun dari temp data
def get_totals_by_year(year):
    total_amount = TempData.query.with_entities(db.func.sum(TempData.amount)).filter_by(year=year).scalar()
    total_energy = TempData.query.with_entities(db.func.sum(TempData.energy)).filter_by(year=year).scalar()
    total_cost = TempData.query.with_entities(db.func.sum(TempData.cost)).filter_by(year=year).scalar()
    total_carbon = TempData.query.with_entities(db.func.sum(TempData.carbon)).filter_by(year=year).scalar()

    return total_amount, total_energy, total_cost, total_carbon

# Function untuk menghitung rate
def calculate_rate(initial_value, final_value):
    if initial_value == 0:
        percentage_increase = 100
    else:
        percentage_increase = ((final_value - initial_value) / initial_value) * 100
    return percentage_increase

# Function untuk mengambil total unit as-is
def get_total_unit():
    total_jumlah_unit = db.session.query(func.sum(CarbonEmission.jumlah_unit)).scalar()
    return total_jumlah_unit

# Function untuk mengambil total unit as-is yang "diperkirakan akan EOL"
def get_total_eol_unit(year):
    total_jumlah_unit = db.session.query(func.sum(CarbonEmission.jumlah_unit)).filter(CarbonEmission.tahun_perolehan <= year).scalar()
    return total_jumlah_unit

# Function untuk mengambil jumlah row
def get_row_count():
    asset_row = db.session.query(CarbonEmission).count()
    loc_row = db.session.query(Location).count()
    category_row = db.session.query(AssetCategory.category_name).distinct().count()
    subcategory_row = db.session.query(AssetCategory.sub_category_name).distinct().count()
    return asset_row, loc_row, category_row, subcategory_row


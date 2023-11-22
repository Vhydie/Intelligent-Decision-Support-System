from flask import jsonify
from apps.models    import *

def location_missing_values(locations):
    for location in locations.items:
        if not location.nama_ruang:
            location.nama_ruang = "-"
        if not location.nama_gedung:
            location.nama_gedung = "-"
            
def json_location(locations):
    return jsonify(locations=[{
            'nama_gedung': location.nama_gedung,
            'nama_ruang': location.nama_ruang
        } for location in locations.items])

def location_searching(searchBy, searchText, query):
    if searchBy == 'building_name':
        query = query.filter(Location.nama_gedung.ilike(f'%{searchText}%'))
    elif searchBy == 'room_name':
        query = query.filter(Location.nama_ruang.ilike(f'%{searchText}%'))
    elif searchBy == 'location_code':
        query = query.filter(Location.kode_lokasi.ilike(f'%{searchText}%'))
    return query

def emission_factors_missing_values(emission_factors):
    for ef in emission_factors.items:
        if not ef.nilai_ef:
            ef.nilai_ef = 0.0
        if not ef.tahun_relevansi_ef:
            ef.tahun_relevansi_ef = 0

def json_emission_factors(emission_factors):
    return jsonify(emission_factors=[{
            'kode_ef': ef.kode_ef,
            'nama_ef': ef.nama_ef,
            'nilai_ef': ef.nilai_ef,
            'tahun_relevansi_ef': ef.tahun_relevansi_ef
        } for ef in emission_factors.items])
    
def emission_factors_searching(searchBy, searchText, query):
    if searchBy == 'kode_ef':
        query = query.filter(EmissionFactors.kode_ef.ilike(f'%{searchText}%'))
    elif searchBy == 'nama_ef':
        query = query.filter(EmissionFactors.nama_ef.ilike(f'%{searchText}%'))
    elif searchBy == 'nilai_ef':
        query = query.filter(EmissionFactors.nilai_ef.ilike(f'%{searchText}%'))
    elif searchBy == 'tahun_relevansi_ef':
        query = query.filter(EmissionFactors.tahun_relevansi_ef.ilike(f'%{searchText}%'))
    return query

def asset_categories_missing_values(asset_categories):
    for ac in asset_categories.items:
        if not ac.asset_ef:
            ac.asset_ef = 0.0
            
def json_asset_categories(asset_categories):
    return jsonify(asset_categories=[{
            'kode_kategori': ac.kode_kategori,
            'major_category_name': ac.major_category_name,
            'category_name': ac.category_name,
            'sub_category_name': ac.sub_category_name,
            'asset_ef': ac.asset_ef
        } for ac in asset_categories.items])
    
def asset_categories_searching(searchBy, searchText, query):
    if searchBy == 'kode_kategori':
        query = query.filter(AssetCategory.kode_kategori.ilike(f'%{searchText}%'))
    elif searchBy == 'major_category_name':
        query = query.filter(AssetCategory.major_category_name.ilike(f'%{searchText}%'))
    elif searchBy == 'category_name':
        query = query.filter(AssetCategory.category_name.ilike(f'%{searchText}%'))
    elif searchBy == 'sub_category_name':
        query = query.filter(AssetCategory.sub_category_name.ilike(f'%{searchText}%'))
    return query

def asset_data_missing_values(asset_data):
    for ad in asset_data.items:
        if not ad.energy:
            ad.energy = 0.0
        if not ad.cost:
            ad.cost = 0.0
        if not ad.carbon:
            ad.carbon = 0.0
            
def json_asset_data(asset_data):
    return jsonify(asset_data=[{
            'nomor_aset': ad.nomor_aset,
            'kode_lokasi': ad.kode_lokasi,
            'unit_kerja': ad.unit_kerja,
            'kode_kategori': ad.kode_kategori,
            'deskripsi': ad.deskripsi,
            'tahun_perolehan': ad.tahun_perolehan,
            'jumlah_unit': ad.jumlah_unit,
            'energy': float(ad.energy),
            'cost': float(ad.cost),
            'carbon': float(ad.carbon)
        } for ad in asset_data.items])
    
def asset_data_searching(searchBy, searchText, query):
    if searchBy == 'nomor_aset':
        query = query.filter(CarbonEmission.nomor_aset.ilike(f'%{searchText}%'))
    elif searchBy == 'kode_lokasi':
        query = query.filter(CarbonEmission.kode_lokasi.ilike(f'%{searchText}%'))
    elif searchBy == 'unit_kerja':
        query = query.filter(CarbonEmission.unit_kerja.ilike(f'%{searchText}%'))
    elif searchBy == 'kode_kategori':
        query = query.filter(CarbonEmission.kode_kategori.ilike(f'%{searchText}%'))
    elif searchBy == 'tahun_perolehan':
        query = query.filter(CarbonEmission.tahun_perolehan.ilike(f'%{searchText}%'))
    return query

def json_emission():
    data_json = []
    data = formatted_data(get_emission_subcategory())
    for row in data:
        data_json.append({
            'tahun_perolehan': row[0],
            'kode_kategori': row[1],
            'jumlah_unit': row[2],
            'energy': row[3],
            'cost': row[4],
            'carbon': row[5]
        })
    return jsonify(data_json)

def emission_searching(searchBy, searchText, data):
    if searchBy == 'tahun_perolehan':
        filtered_data = [row for row in data if str(row[0]).lower().find(searchText.lower()) != -1]
    elif searchBy == 'category_name':
        filtered_data = [row for row in data if str(row[1]).lower().find(searchText.lower()) != -1]
    elif searchBy == 'sub_category_name':
        filtered_data = [row for row in data if str(row[1]).lower().find(searchText.lower()) != -1]
    elif searchBy == 'jumlah_unit':
        filtered_data = [row for row in data if str(row[2]).lower().find(searchText.lower()) != -1]
    elif searchBy == 'energy':
        filtered_data = [row for row in data if str(row[3]).lower().find(searchText.lower()) != -1]
    elif searchBy == 'cost':
        filtered_data = [row for row in data if str(row[4]).lower().find(searchText.lower()) != -1]
    elif searchBy == 'carbon':
        filtered_data = [row for row in data if str(row[5]).lower().find(searchText.lower()) != -1]
    else:
        filtered_data = data

    return filtered_data

def json_emission_categroy():
    data_json = []
    data = formatted_data(get_emission_category())
    for row in data:
        data_json.append({
            'tahun_perolehan': row[0],
            'kode_kategori': row[1],
            'jumlah_unit': row[2],
            'energy': row[3],
            'cost': row[4],
            'carbon': row[5]
        })
    return jsonify(data_json)

def get_current_electricity_id():
    # Mengambil current_electricity_id
    last_electricity_id = EmissionFactors.query.filter(EmissionFactors.kode_ef.like('EFEL%')).order_by(EmissionFactors.kode_ef.desc()).first()
    if last_electricity_id:
        current_electricity_id = int(last_electricity_id.kode_ef[4:]) + 1
        current_electricity_id = "EFEL{:04d}".format(current_electricity_id)
    else:
        current_electricity_id = "EFEL0001"
    return current_electricity_id

def get_current_carbon_id():
    # Mengambil current_carbon_id
    last_carbon_id = EmissionFactors.query.filter(EmissionFactors.kode_ef.like('EFCE%')).order_by(EmissionFactors.kode_ef.desc()).first()
    if last_carbon_id:
        current_carbon_id = int(last_carbon_id.kode_ef[4:]) + 1
        current_carbon_id = "EFCE{:04d}".format(current_carbon_id)
    else:
        current_carbon_id = "EFCE0001"
    return current_carbon_id
        
def get_major_category_from_major_category_name(major_category_name):
    asset_category = AssetCategory.query.filter_by(major_category_name=major_category_name).first()
    if asset_category:
        return asset_category.major_category
    else:
        return None
    
def get_category_from_category_name(category_name):
    asset_category = AssetCategory.query.filter_by(category_name=category_name).first()
    if asset_category:
        return asset_category.category
    else:
        return None
      
def get_category_from_sub_category_name(sub_category_name):
    asset_category = AssetCategory.query.filter_by(category_name=sub_category_name).first()
    if asset_category:
        return asset_category.category
    else:
        return None
        
def get_sub_category_from_category(category):
    highest_sub_category = AssetCategory.query.filter_by(category=category).order_by(AssetCategory.sub_category.desc()).first()
    
    if highest_sub_category:
        highest_sub_category_num = int(highest_sub_category.sub_category)
        next_sub_category = highest_sub_category_num + 1
    else:
        next_sub_category = 1
    
    return str(next_sub_category).zfill(4)
        
def generate_category_code(major_category_name, category_name, sub_category_name, include_sleep):
    major_category = major_category_name[:3].upper()
    category = category_name[:3].upper()
    if include_sleep:
        sub_category = '0001'
    else:
        sub_category = sub_category_name[:4].upper()

    category_code = f"{major_category}.{category}.{sub_category}"
    return category_code


# Function untuk initiatives
# Function untuk initiatives
# Function untuk initiatives
# Generate Electronic Waste Count
def electronic_waste(df, year):
    count_comp, count_server, count_telp, count_av, count_imaging, count_network = 0, 0, 0, 0, 0, 0
    for data in df:
        if data[1] == "Komputer" and data[0] <= year-7:
            count_comp += data[3]
        elif data[1] == "Server" and data[0] <= year-10:
            count_server += data[3]
        elif data[1] == "Telepon" and data[0] <= year-4:
            count_telp += data[3]
        elif data[1] == "Audio Visual" and data[0] <= year-5:
            count_av += data[3]
        elif data[1] == "Pemrosesan Gambar" and data[0] <= year-5:
            count_imaging += data[3]
        elif data[1] == "Jaringan" and data[0] <= year-5:
            count_network += data[3]
    result = [count_comp, count_server, count_telp, count_av, count_imaging, count_network]
    return result, sum(result)

# Generate initiatives
def alternative_initiatives(unit_rate, waste, unit_not_waste_decimal, emission_rate):
    initiatives_prio1 = ["Landfill", "Reuse", "Recycling", "Reduction", "Repair", "Energy Recovery", "Avoidance"]
    initiatives_prio2 = ["Reuse", "Reduction", "Repair", "Landfill", "Recycling", "Energy Recovery", "Avoidance"]
    unit_not_waste = int(unit_not_waste_decimal)
    unit_threshold = 0.124
    emssion_threshold = 0.03986
    emission_middle_threshold = 0.02
    initiatives = []
    
    # Penentuan initiatives
    if unit_rate <= unit_threshold: # initiatives_prio1
        initiatives_used = initiatives_prio1
    else:   # initiatives_prio2
        initiatives_used = initiatives_prio2
        
    if (waste >= unit_not_waste):
        if (emission_rate >= emission_middle_threshold):
            initiatives.append(initiatives_used[0])
            initiatives.append(initiatives_used[1])
            initiatives.append(initiatives_used[2])
        else:
            initiatives.append(initiatives_used[1])
            initiatives.append(initiatives_used[0])
            initiatives.append(initiatives_used[3])
    elif (waste >= (0.5*unit_not_waste)):
        if (emission_rate >= emssion_threshold):
            initiatives.append(initiatives_used[2])
            initiatives.append(initiatives_used[0])
            initiatives.append(initiatives_used[1])
        elif (emission_rate >= 0):
            initiatives.append(initiatives_used[3])
            initiatives.append(initiatives_used[0])
            initiatives.append(initiatives_used[1])
        else:
            initiatives.append(initiatives_used[4])
            initiatives.append(initiatives_used[1])
            initiatives.append(initiatives_used[0])
    else:
        if (emission_rate >= emission_middle_threshold):
            initiatives.append(initiatives_used[5])
            initiatives.append(initiatives_used[2])
            initiatives.append(initiatives_used[0])
        else:
            initiatives.append(initiatives_used[6])
            initiatives.append(initiatives_used[3])
            initiatives.append(initiatives_used[0])
    
    return initiatives

# Function untuk deskripsi initiatives
def initiative_desc(initiatives):
    descs = []
    practices = []
    for initiative in initiatives:
        if initiative == "Landfill":
            descs.append("Seluruh unit yang sudah masuk masa EOL dibuang jika tidak digunakan aktif.")
            practices.append("Hapus informasi penting di perangkat Anda sebelum membuang barang, serta bedakan tempat pembuangannya.")
        elif initiative == "Reuse":
            descs.append("Gunakan kembali sebagian unit yang sudah masuk masa EOL, sisanya dapat dibuang.")
            practices.append("Anda dapat menggunakan kembali peralatan lama yang masih dapat berfungsi dengan baik dalam melakukan pekerjaannya.")
        elif initiative == "Recycling":
            descs.append("Daur ulang material yang dapat didaur ulang dari seluruh unit yang sudah masa EOL.")
            practices.append("Perhatikan material berbahaya yang mungkin terdapat dalam perangkat Anda ketika Anda ingin memilah materialnya.")
        elif initiative == "Reduction":
            descs.append("Kurangi pengadaan peralatan TI di masa depan, tanpa mengganggu unit yang sudah masa EOL.")
            practices.append("Lihat peralatan yang Anda punya saat ini dan kurangi pengadaan untuk peralatan yang menurut Anda masih layak pakai.")
        elif initiative == "Repair":
            descs.append("Perbaiki sebagian unit yang sudah masuk masa EOL sehingga dapat digunakan kembali.")
            practices.append("Perbaiki peralatan yang masih dapat diperbaiki, namun pastikan keamanan informasi terjaga bila memakai bantuan pihak ketiga.")
        elif initiative == "Energy Recovery":
            descs.append("Bakar seluruh unit masa EOL sehingga dapat digunakan sebagai energi terbarukan.")
            practices.append("Pastikan keputusan pembakaran peralatan ini tepat untuk dilakukan. Beberapa peralatan mungkin berbahaya jika dibakar.")
        elif initiative == "Avoidance":
            descs.append("Abaikan seluruh unit yang telah memasuki masa EOL jika masih digunakan aktif.")
            practices.append("Meskipun diabaikan, jangan terlalu gegabah untuk melakukan pengadaan peralatan yang sangat besar.")
        
    return descs, practices

# Function untuk informasi alternatif
def initative_action(initiatives, unit_predicted_decimal, waste_decimal):
    unit_predicted = int(unit_predicted_decimal)
    waste = int(waste_decimal)
    units = []
    disposed = []
    procured = []
    for initiative in initiatives:
        if initiative == "Landfill":
            units.append(waste)
            disposed.append(waste)
            procured.append(unit_predicted)
        elif initiative == "Reuse":
            units.append(round(unit_predicted*0.4))
            disposed.append(round(unit_predicted*0.4))
            procured.append(round(unit_predicted*0.6))
        elif initiative == "Recycling":
            units.append(round(waste*0.2))
            disposed.append(waste)
            procured.append(unit_predicted)
        elif initiative == "Reduction":
            units.append(round(unit_predicted*0.3))
            disposed.append(0)
            procured.append(round(unit_predicted*0.7))
        elif initiative == "Repair":
            units.append(round(unit_predicted*0.2))
            disposed.append(round(unit_predicted*0.2))
            procured.append(round(unit_predicted*0.8))
        elif initiative == "Energy Recovery":
            units.append(waste)
            disposed.append(waste)
            procured.append(unit_predicted)
        elif initiative == "Avoidance":
            units.append(waste)
            disposed.append(0)
            procured.append(unit_predicted)
        
    return units, disposed, procured

# Function untuk memberi total unit, energy, cost, dan carbon
def predictions_group_by_year(predictions):
    result = {}
    for prediction in predictions:
        year, category, subcategory, energy, cost, carbon, unit = prediction
        energy = float(energy)
        cost = float(cost)
        carbon = float(carbon)
        unit = float(unit)
        
        if year in result:
            result[year] = [result[year][0] + unit, result[year][1] + energy, result[year][2] + cost, result[year][3] + carbon]
        else:
            result[year] = [unit, energy, cost, carbon]

    result = [[year] + values for year, values in result.items()]
    for i in range(1, len(result)):
        prev_values = result[i - 1][1:]
        curr_values = result[i][1:]
        rates = [((curr - prev) / prev) * 100 if prev != 0 else 0 for curr, prev in zip(curr_values, prev_values)]
        result[i].extend(rates)

    return result

# Function filter data by subcategory
def filter_data_by_subcategory(data, subcategory):
    result = []
    for item in data:
        if item[2] == subcategory:
            result.append(item)
    return result

# Function filter data by category
def filter_data_by_category(data, category):
    result = []
    for item in data:
        if item[1] == category:
            result.append(item)
    return result
from database import SessionLocal
import models

# (name, category, [models])
BRANDS = [
    ("Fiat",            "car",         ["Uno", "Palio", "Siena", "Strada", "Toro", "Pulse", "Cronos", "Mobi", "Argo", "Fastback"]),
    ("Chevrolet",       "car",         ["Onix", "Tracker", "S10", "Montana", "Spin", "Equinox", "Trailblazer", "Cruze"]),
    ("Volkswagen",      "car",         ["Gol", "Polo", "Virtus", "T-Cross", "Nivus", "Saveiro", "Amarok", "Taos"]),
    ("Toyota",          "car",         ["Corolla", "Hilux", "SW4", "Yaris", "RAV4", "Corolla Cross", "Camry"]),
    ("Hyundai",         "car",         ["HB20", "Creta", "Tucson", "Santa Fe", "i30", "Elantra"]),
    ("Renault",         "car",         ["Kwid", "Sandero", "Logan", "Duster", "Captur", "Oroch", "Kardian"]),
    ("Honda",           "car",         ["Civic", "City", "HR-V", "CR-V", "WR-V", "Fit", "Accord"]),
    ("Jeep",            "car",         ["Renegade", "Compass", "Commander", "Wrangler", "Gladiator"]),
    ("Nissan",          "car",         ["Kicks", "Frontier", "Versa", "Sentra", "March"]),
    ("Ford",            "car",         ["Ka", "EcoSport", "Ranger", "Bronco", "Territory", "Maverick"]),
    ("Mitsubishi",      "car",         ["ASX", "Eclipse Cross", "Outlander", "L200", "Pajero"]),
    ("Citroën",         "car",         ["C3", "C4 Cactus", "Aircross", "Jumpy"]),
    ("Peugeot",         "car",         ["208", "2008", "3008", "408", "Partner"]),
    ("BMW",             "car",         ["Serie 3", "Serie 5", "X1", "X3", "X5", "M3", "Z4"]),
    ("Mercedes-Benz",   "car",         ["Classe A", "Classe C", "Classe E", "GLA", "GLC", "AMG"]),
    ("Audi",            "car",         ["A3", "A4", "Q3", "Q5", "TT", "RS3"]),
    ("Kia",             "car",         ["Sportage", "Sorento", "Stinger", "Cerato", "Carnival"]),
    ("Caoa Chery",      "car",         ["Tiggo 2", "Tiggo 5x", "Tiggo 7", "Tiggo 8", "Arrizo 6"]),
    ("BYD",             "car",         ["Dolphin", "Seal", "Han", "Tang", "Atto 3", "King"]),
    ("Ram",             "car",         ["1500", "2500", "Rampage"]),
    ("Honda Motos",     "motorcycle",  ["CG 160", "CB 300", "CB 500", "XRE 300", "PCX", "Biz", "Pop", "Titan"]),
    ("Yamaha",          "motorcycle",  ["Factor", "Fazer 250", "MT-03", "MT-07", "Lander", "Crosser", "NMAX"]),
    ("Suzuki",          "motorcycle",  ["GSX", "V-Strom", "Burgman", "Intruder", "Boulevard"]),
    ("Kawasaki",        "motorcycle",  ["Ninja 300", "Ninja 400", "Z400", "Versys", "Vulcan"]),
    ("BMW Motorrad",    "motorcycle",  ["G 310", "F 850", "R 1250", "S 1000"]),
    ("Harley-Davidson", "motorcycle",  ["Sportster", "Iron 883", "Fat Boy", "Road King", "Street Glide"]),
    ("Royal Enfield",   "motorcycle",  ["Meteor 350", "Himalayan", "Classic 350", "Interceptor 650"]),
]


def seed():
    db = SessionLocal()
    try:
        # Nullify vehicle FK references to allow safe deletion
        for v in db.query(models.Vehicle).all():
            v.brand_id = None
            v.model_id = None
        db.flush()

        db.query(models.VehicleModel).delete()
        db.query(models.Brand).delete()
        db.flush()

        created_brands = 0
        created_models = 0
        for brand_name, category, model_names in BRANDS:
            brand = models.Brand(name=brand_name, category=category)
            db.add(brand)
            db.flush()
            created_brands += 1

            for model_name in model_names:
                db.add(models.VehicleModel(name=model_name, brand_id=brand.id))
                created_models += 1

        db.commit()
        print(f"Seed concluído: {created_brands} marcas e {created_models} modelos criados.")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

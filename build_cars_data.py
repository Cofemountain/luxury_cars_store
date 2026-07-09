import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

BRANDS = {
    "aston_martin": {
        "cars": [
            {
                "folder": "aston_martin",
                "car_id": "car1",
                "title": "Aston Martin Vantage S",
                "slug": "aston_martin_vantage_s",
                "price": "18 500 000 ₽",
            },
            {
                "folder": "Aston Martin Valhalla",
                "car_id": "car2",
                "title": "Aston Martin Valhalla",
                "slug": "aston_martin_valhalla",
                "price": "45 000 000 ₽",
            },
        ],
    },
    "bugatti": {
        "cars": [
            {
                "folder": "Buggati",
                "car_id": "car1",
                "title": "Bugatti Vision Gran Turismo",
                "slug": "bugatti_vision_gt",
                "price": "120 000 000 ₽",
                "override_specs": {
                    "Марка и модель": "Bugatti Vision Gran Turismo",
                    "Тип кузова": "Купе",
                    "Двигатель": "8.0 л, W16, бензиновый, четырёхтурбинный",
                    "Мощность": "1650 л.с.",
                    "Крутящий момент": "1600 Н·м",
                    "Коробка передач": "7-ступенчатая роботизированная",
                    "Привод": "Полный",
                    "Разгон 0–100 км/ч": "2.4 сек",
                    "Максимальная скорость": "420 км/ч",
                    "Сухая масса": "1900 кг",
                },
            },
            {
                "folder": "bugatti veyron",
                "car_id": "car2",
                "title": "Bugatti Veyron 16.4",
                "slug": "bugatti_veyron",
                "price": "150 000 000 ₽",
            },
        ],
    },
    "ferrari": {
        "cars": [
            {
                "folder": "Ferrari",
                "car_id": "car1",
                "title": "Ferrari FXX K",
                "slug": "ferrari_fxx_k",
                "price": "85 000 000 ₽",
            },
            {
                "folder": "Ferrari SF90 Stradale",
                "car_id": "car2",
                "title": "Ferrari SF90 Stradale",
                "slug": "ferrari_sf90_stradale",
                "price": "38 000 000 ₽",
            },
        ],
    },
    "lamborghini": {
        "cars": [
            {
                "folder": "lamborgini",
                "car_id": "car1",
                "title": "Lamborghini Huracán",
                "slug": "lamborghini_huracan",
                "price": "32 000 000 ₽",
            },
            {
                "folder": "Lamborghini Revuelto",
                "car_id": "car2",
                "title": "Lamborghini Revuelto",
                "slug": "lamborghini_revuelto",
                "price": "52 000 000 ₽",
            },
        ],
    },
    "mclaren": {
        "cars": [
            {
                "folder": "McLaren_650S",
                "car_id": "car1",
                "title": "McLaren 650S",
                "slug": "mclaren_650s",
                "price": "24 500 000 ₽",
            },
            {
                "folder": "McLaren P1",
                "car_id": "car2",
                "title": "McLaren P1",
                "slug": "mclaren_p1",
                "price": "89 000 000 ₽",
            },
        ],
    },
    "porsche": {
        "cars": [
            {
                "folder": "Porsche_911",
                "car_id": "car1",
                "title": "Porsche 911 GT3 Touring",
                "slug": "porsche_911_gt3_touring",
                "price": "22 000 000 ₽",
            },
            {
                "folder": "Porsche_718",
                "car_id": "car2",
                "title": "Porsche 718 Cayman",
                "slug": "porsche_718_cayman",
                "price": "12 500 000 ₽",
            },
        ],
    },
}


def load_existing_cars_data():
    path = os.path.join(ROOT, "card", "cars_data.js")
    if not os.path.isfile(path):
        return {}

    with open(path, encoding="utf-8") as f:
        content = f.read().strip()

    if content.startswith("const carsData = "):
        content = content[len("const carsData = "):]

    if content.endswith(";"):
        content = content[:-1]

    return json.loads(content)


def get_specs(car_meta, existing_car):
    if existing_car and existing_car.get("specs"):
        return existing_car["specs"]

    overrides = car_meta.get("override_specs")
    if overrides:
        return build_specs(overrides)

    return []
def build_specs(specs_map):
    normalized = {}

    for key, value in specs_map.items():
        if key == "Марка и модель" or not value:
            continue

        lower = key.lower()
        if "разгон" in lower:
            normalized["Разгон 0-100 км/ч"] = value
        elif lower in ("максимальная скорость", "макс. скорость"):
            normalized["Макс. скорость"] = value
        elif lower in ("мощность", "мощность двигателя"):
            normalized["Мощность двигателя"] = value
        elif lower in ("двигатель", "тип двигателя"):
            normalized["Тип двигателя"] = value
        elif key not in normalized:
            normalized[key] = value

    order = [
        "Разгон 0-100 км/ч",
        "Макс. скорость",
        "Мощность двигателя",
        "Крутящий момент",
        "Тип двигателя",
        "Коробка передач",
        "Привод",
        "Тип кузова",
        "Снаряжённая масса",
        "Сухая масса",
    ]

    specs = []
    for name in order:
        if name not in normalized:
            continue
        specs.append({
            "name": name,
            "value": normalized[name],
            "highlight": name == "Разгон 0-100 км/ч",
        })

    return specs


def ensure_cover_image(folder_path):
    cover_names = {"1.jpg", "1.jpeg", "1.png", "1.webp", "1.avif"}
    existing = {
        name.lower()
        for name in os.listdir(folder_path)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    }

    if existing & cover_names:
        return

    images = sorted(
        name
        for name in os.listdir(folder_path)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    )
    if not images:
        return

    source = os.path.join(folder_path, images[0])
    ext = os.path.splitext(images[0])[1].lower()
    target = os.path.join(folder_path, f"1{ext}")
    if not os.path.exists(target):
        shutil.copy2(source, target)


def image_paths(folder):
    folder_path = os.path.join(ASSETS, folder)
    ensure_cover_image(folder_path)
    files = [
        name
        for name in os.listdir(folder_path)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    ]

    def sort_key(name):
        stem = os.path.splitext(name)[0]
        if stem.isdigit():
            return (0, int(stem), name.lower())
        return (1, 999, name.lower())

    files.sort(key=sort_key)
    return [f"../assets/{folder}/{name}" for name in files]


def main():
    existing_data = load_existing_cars_data()
    cars_data = {}

    for brand_id, brand_meta in BRANDS.items():
        cars_data[brand_id] = {}

        for car_meta in brand_meta["cars"]:
            folder = car_meta["folder"]
            car_id = car_meta["car_id"]
            existing_car = existing_data.get(brand_id, {}).get(car_id, {})

            cars_data[brand_id][car_id] = {
                "title": car_meta["title"],
                "price": car_meta["price"],
                "preorderUrl": f"../preorder.html?car={car_meta['slug']}",
                "images": image_paths(folder),
                "specs": get_specs(car_meta, existing_car),
            }

    output_path = os.path.join(ROOT, "card", "cars_data.js")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("const carsData = ")
        f.write(json.dumps(cars_data, ensure_ascii=False, indent=2))
        f.write(";\n")

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

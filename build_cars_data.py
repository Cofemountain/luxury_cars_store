import json
import os

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


def parse_data_txt(path, overrides=None):
    specs_map = {}
    if overrides:
        specs_map.update(overrides)
    elif os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                key, value = line.split(":", 1)
                specs_map[key.strip()] = value.strip()
    return specs_map


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


def image_paths(folder):
    folder_path = os.path.join(ASSETS, folder)
    files = [
        name
        for name in os.listdir(folder_path)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    ]

    def sort_key(name):
        stem = os.path.splitext(name)[0]
        if stem == "1":
            return (0, name.lower())
        return (1, name.lower())

    files.sort(key=sort_key)
    return [f"../assets/{folder}/{name}" for name in files]


def main():
    cars_data = {}

    for brand_id, brand_meta in BRANDS.items():
        cars_data[brand_id] = {}

        for car_meta in brand_meta["cars"]:
            folder = car_meta["folder"]
            car_id = car_meta["car_id"]
            data_path = os.path.join(ASSETS, folder, "data.txt")
            overrides = car_meta.get("override_specs")
            specs_map = parse_data_txt(data_path, overrides)

            cars_data[brand_id][car_id] = {
                "title": car_meta["title"],
                "price": car_meta["price"],
                "preorderUrl": f"../preorder.html?car={car_meta['slug']}",
                "images": image_paths(folder),
                "specs": build_specs(specs_map),
            }

    output_path = os.path.join(ROOT, "card", "cars_data.js")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("const carsData = ")
        f.write(json.dumps(cars_data, ensure_ascii=False, indent=2))
        f.write(";\n")

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

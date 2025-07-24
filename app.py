from flask import Flask, request, jsonify
from flask_cors import CORS
from skyfield.api import load, Topos
from skyfield.data import hipparcos

app = Flask(__name__)
CORS(app) 

# تحميل البيانات الفلكية
planets = load('de421.bsp')
ts = load.timescale()
earth = planets['earth']

# تحميل النجوم الساطعة من كتالوج Hipparcos
with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)

# اختيار نجوم معروفة
named_stars = {
    "Sirius": 32349,
    "Betelgeuse": 27989,
    "Vega": 91262,
    "Altair": 97649,
    "Rigel": 24436
}

@app.route("/api/astro")
def astro_data():
    lat = float(request.args.get("lat", 23.6))   # default: Muscat
    lng = float(request.args.get("lng", 58.5))

    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lng)
    t = ts.now()

    result = {
        "datetime": t.utc_iso(),
        "location": {"lat": lat, "lng": lng},
        "sun_moon_planets": {},
        "stars": {}
    }

    # الشمس، القمر، والكواكب
    bodies = {
        "Sun": "sun",
        "Moon": "moon",
        "Mercury": "mercury",
        "Venus": "venus",
        "Mars": "mars",
        "Jupiter": "jupiter barycenter",
        "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter",
        "Neptune": "neptune barycenter",
        "Pluto": "pluto barycenter"
    }

    for name, key in bodies.items():
        body = planets[key]
        astrometric = observer.at(t).observe(body).apparent()
        alt, az, distance = astrometric.altaz()
        result["sun_moon_planets"][name] = {
            "altitude_deg": round(alt.degrees, 2),
            "azimuth_deg": round(az.degrees, 2),
            "distance_au": round(distance.au, 5)
        }

    # بعض النجوم المعروفة
    for name, hip_id in named_stars.items():
        star = stars.loc[hip_id]
        astrometric = observer.at(t).observe(star).apparent()
        alt, az, _ = astrometric.altaz()
        result["stars"][name] = {
            "altitude_deg": round(alt.degrees, 2),
            "azimuth_deg": round(az.degrees, 2)
        }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from skyfield.api import load, Topos
from skyfield.data import hipparcos
from skyfield.starlib import Star

app = Flask(__name__)
CORS(app)

planets = load('de421.bsp')
ts = load.timescale()
earth = planets['earth']

# بيانات الكواكب الثابتة
planet_info = {
    "Mercury": {"mass_kg": 3.3011e23, "mass_earths": 0.055, "radius_km": 2439.7, "moons": 0, "orbital_period_days": 88, "day_length_hours": 1407.6},
    "Venus":   {"mass_kg": 4.8675e24, "mass_earths": 0.815, "radius_km": 6051.8, "moons": 0, "orbital_period_days": 225, "day_length_hours": 5832.5},
    "Earth":   {"mass_kg": 5.97237e24,"mass_earths": 1,     "radius_km": 6371.0, "moons": 1, "orbital_period_days": 365.25,"day_length_hours": 24},
    "Mars":    {"mass_kg": 6.4171e23, "mass_earths": 0.107, "radius_km": 3389.5, "moons": 2, "orbital_period_days": 687,   "day_length_hours": 24.6},
    "Jupiter": {"mass_kg": 1.8982e27, "mass_earths": 317.8, "radius_km": 69911,  "moons": 92,"orbital_period_days": 4331,  "day_length_hours": 9.9},
    "Saturn":  {"mass_kg": 5.6834e26, "mass_earths": 95.2,  "radius_km": 58232,  "moons": 83,"orbital_period_days": 10747, "day_length_hours": 10.7},
    "Uranus":  {"mass_kg": 8.6810e25, "mass_earths": 14.5,  "radius_km": 25362,  "moons": 27,"orbital_period_days": 30589, "day_length_hours": 17.2},
    "Neptune": {"mass_kg": 1.02413e26,"mass_earths": 17.1,  "radius_km": 24622,  "moons": 14,"orbital_period_days": 59800, "day_length_hours": 16.1}
}

# النجوم
with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)

named_stars = {
    "Sirius": 32349,
    "Betelgeuse": 27989,
    "Vega": 91262,
    "Altair": 97649,
    "Rigel": 24436
}

@app.route("/api/astro")
def astro_data():
    lat = float(request.args.get("lat", 23.6))
    lng = float(request.args.get("lng", 58.5))
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lng)
    t = ts.now()

    result = {
        "datetime": t.utc_iso(),
        "location": {"lat": lat, "lng": lng},
        "sun_moon_planets": {},
        "stars": {}
    }

    bodies = {
        "Sun": "sun", "Moon": "moon",
        "Mercury": "mercury", "Venus": "venus", "Mars": "mars",
        "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter", "Neptune": "neptune barycenter",
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

    for name, hip_id in named_stars.items():
        if hip_id not in stars.index:
            continue
        row = stars.loc[hip_id]
        star = Star(ra_hours=row['ra_hours'], dec_degrees=row['dec_degrees'])
        astrometric = observer.at(t).observe(star).apparent()
        alt, az, _ = astrometric.altaz()
        result["stars"][name] = {
            "altitude_deg": round(alt.degrees, 2),
            "azimuth_deg": round(az.degrees, 2)
        }

    return jsonify(result)

@app.route("/api/planets")
def get_planet_list():
    return jsonify(list(planet_info.keys()))

@app.route("/api/planet/<name>")
def planet_details(name):
    lat = float(request.args.get("lat", 23.6))
    lng = float(request.args.get("lng", 58.5))
    t = ts.now()
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lng)

    try:
        body = planets[name.lower()] if name.lower() in planets else planets[name]
    except:
        return jsonify({"error": "Invalid planet name"}), 404

    astro = observer.at(t).observe(body).apparent()
    alt, az, dist = astro.altaz()

    info = planet_info.get(name.capitalize(), {})
    return jsonify({
        "name": name.capitalize(),
        "altitude_deg": round(alt.degrees, 2),
        "azimuth_deg": round(az.degrees, 2),
        "distance_au": round(dist.au, 5),
        "mass_kg": info.get("mass_kg"),
        "mass_earths": info.get("mass_earths"),
        "radius_km": info.get("radius_km"),
        "moons": info.get("moons"),
        "orbital_period_days": info.get("orbital_period_days"),
        "day_length_hours": info.get("day_length_hours"),
        "datetime": t.utc_iso()
    })

if __name__ == "__main__":
    app.run(debug=True)

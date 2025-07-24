from flask import Flask, jsonify
from skyfield.api import load, Topos

app = Flask(__name__)

ts = load.timescale()
eph = load('de421.bsp')

# مسقط، عمان
observer = eph['earth'].topos(latitude_degrees=23.6, longitude_degrees=58.5)

@app.route('/api/sun')
def sun_position():
    t = ts.now()
    astrometric = observer.at(t).observe(eph['sun']).apparent()
    alt, az, distance = astrometric.altaz()
    return jsonify({
        'altitude_deg': round(alt.degrees, 2),
        'azimuth_deg': round(az.degrees, 2),
        'distance_au': round(distance.au, 6)
    })

@app.route('/api/moon')
def moon_position():
    t = ts.now()
    astrometric = observer.at(t).observe(eph['moon']).apparent()
    alt, az, distance = astrometric.altaz()
    return jsonify({
        'altitude_deg': round(alt.degrees, 2),
        'azimuth_deg': round(az.degrees, 2),
        'distance_au': round(distance.au, 6)
    })

@app.route('/api/planets')
def planets_positions():
    t = ts.now()
    planet_names = [
        'mercury', 'venus', 'mars',
        'jupiter barycenter', 'saturn barycenter',
        'uranus barycenter', 'neptune barycenter'
    ]
    results = {}
    for name in planet_names:
        planet = eph[name]
        astrometric = observer.at(t).observe(planet).apparent()
        alt, az, distance = astrometric.altaz()
        results[name.title()] = {
            'altitude_deg': round(alt.degrees, 2),
            'azimuth_deg': round(az.degrees, 2),
            'distance_au': round(distance.au, 6)
        }
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

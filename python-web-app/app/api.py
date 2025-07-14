from flask import Blueprint, request, jsonify
from flask_login import login_required
from database import get_connection

api = Blueprint('api', __name__)


@api.route('/api/dashboard/Sume', methods=['GET'])
@login_required
def get_summary():
    # print("TEEEEEEEEEEEEEEEEEEEEEEESTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    querry = """
        SELECT
            SUM(Consum_kWh) AS total_consum,
            AVG(Consum_kWh) AS mediu_consum
        FROM consum_energie
        WHERE DataCitire BETWEEN %s AND %s
    """
    cursor.execute(querry, (start_date, end_date))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return jsonify(result)


@api.route('/api/dashboard/top5', methods=['GET'])
@login_required
def get_top_consumatori():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT ClientID, SUM(Consum_kWh) AS total
    FROM consum_energie
    WHERE DataCitire BETWEEN %s AND %s
    GROUP BY ClientID
    ORDER BY total DESC
    LIMIT 5
"""
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


@api.route('/api/dashboard/defect', methods=['GET'])
@login_required
def get_alerte():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT c.ClientID
        FROM consum_energie c
        JOIN consum_energie s ON s.ClientID = c.ClientID
        WHERE s.StatusContor = 'defect'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


@api.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'pong': True})

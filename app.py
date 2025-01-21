import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from dotenv import load_dotenv
from netflow import generate_netflow_data
from analysis import aggregate_netflow_data, calculate_traffic_rate, top_talkers
import plotly.graph_objects as go
from pandas import DataFrame
import json

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///netflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', True) == "True"
db = SQLAlchemy(app)
api = Api(app)


class Netflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    src_ip = db.Column(db.String(15))
    dst_ip = db.Column(db.String(15))
    src_port = db.Column(db.Integer)
    dst_port = db.Column(db.Integer)
    protocol = db.Column(db.String(10))
    bytes = db.Column(db.Integer)
    timestamp = db.Column(db.String(20))

    def __repr__(self):
        return f"<Netflow(src_ip={self.src_ip}, dst_ip={self.dst_ip}, bytes={self.bytes}, timestamp={self.timestamp})>"


class TrafficStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20))
    total_bytes = db.Column(db.Integer)

def generate_plot(df: DataFrame):

    fig = go.Figure(data=[go.Bar(x=df['src_ip'], y=df['bytes'])])

    fig.update_layout(
        title="Top Traffic by Source IP",
        xaxis_title="Source IP",
        yaxis_title="Bytes"
    )
    return json.dumps(fig.to_dict())


@app.route('/')
def index():

    netflow_data = Netflow.query.all()
    aggregated_traffic = aggregate_netflow_data(netflow_data)

    rate_result = calculate_traffic_rate(netflow_data)
    top_result = top_talkers(netflow_data)

    if top_result is not None:
      top_df = DataFrame(top_result)
      top_graph_json = generate_plot(top_df)
    else:
      top_graph_json = None

    return render_template('index.html',
                            aggregated_traffic=aggregated_traffic,
                            traffic_rate=rate_result,
                            top_talkers=top_result,
                            top_graph_json=top_graph_json)


class NetflowData(Resource):
    def get(self):
        netflow_data = Netflow.query.all()
        return jsonify([
            {
                'src_ip': flow.src_ip,
                'dst_ip': flow.dst_ip,
                'src_port': flow.src_port,
                'dst_port': flow.dst_port,
                'protocol': flow.protocol,
                'bytes': flow.bytes,
                'timestamp': flow.timestamp
             } for flow in netflow_data
        ])


api.add_resource(NetflowData, '/netflow')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Populate some dummy data in db
        for i in range(10):
             for item in generate_netflow_data():
                 flow = Netflow(src_ip=item["src_ip"], dst_ip=item['dst_ip'],
                               src_port=item['src_port'], dst_port=item['dst_port'],
                               protocol=item['protocol'], bytes=item['bytes'],
                               timestamp=item['timestamp'])

                 db.session.add(flow)

        db.session.commit()
    app.run()

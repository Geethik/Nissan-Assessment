from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import json
import eventlet

eventlet.monkey_patch()
app = Flask(__name__)

#Connect to MQTT and keep pinging for update
app.config['MQTT_BROKER_URL'] = 'm13.cloudmqtt.com'
app.config['MQTT_BROKER_PORT'] = 13398
app.config['MQTT_USERNAME'] = 'vdgscytv'
app.config['MQTT_PASSWORD'] = 'YJXtFQICixgS'
app.config['MQTT_REFRESH_TIME'] = 1.0  
app.config['MQTT_KEEPALIVE'] = 5
app.config['TEMPLATES_AUTO_RELOAD'] = True

#MQTT protocol connection and SocketIO
mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

#Render index.html
@app.route("/")
def index():
    return render_template("index.html")

#Publish and subscribe messages
@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])

#MQTT connection and message functions
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('owntracks/vdgscytv/80332C50-7851-4EB2-88A2-E14FB5F211A8')
    #Test topic
    #mqtt.subscribe('test')
    
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit('mqtt_message', data=data)
    payload = message.payload.decode()
    #Debug output
    #print payload
    
@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

#Run the app by using the server.py
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8080, use_reloader=True, debug=True)
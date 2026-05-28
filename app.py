from flask import Flask, render_template
from datetime import datetime
import json
from collector import collect_metrics

app = Flask(__name__)

cpu_history = []
mem_history = []


@app.route("/")

def metrics():

    global cpu_history
    global mem_history

    with open("devices.json") as f:

        devices = json.load(f)["devices"]

    device_count = len(devices)

    last_updated = datetime.now().strftime("%H:%M:%S")

    output = []

    for d in devices:

        data = collect_metrics(

            d["host"],
            d["port"],
            d["username"],
            d["password"]

        )

        
        if data["status"] == "OFFLINE":

            output.append({

                "device": d["name"],

                "status": "OFFLINE",

                "cpu": "N/A",

                "memory": "N/A",

                "disk": "N/A",

                "uptime": "Device unreachable",

                "routes": [],

                "ports": [],

                "alerts": ["DEVICE DOWN"]

            })

            continue

       

        cpu = float(data["cpu"])

        mem = float(data["memory"])

        cpu_history.append(cpu)

        mem_history.append(mem)

        cpu_history = cpu_history[-20:]

        mem_history = mem_history[-20:]

        alerts = []

        if cpu > 80:
            alerts.append("HIGH CPU USAGE")

        if mem > 80:
            alerts.append("HIGH MEMORY USAGE")

        routes = data["routes"].split("\n")

        ports = []

        for line in data["ports"].split("\n")[1:]:

            parts = line.split()

            if len(parts) >= 5:

                ports.append({

                    "protocol": parts[0],

                    "state": parts[1],

                    "local": parts[4]

                })

        output.append({

            "device": d["name"],

            "status": "ONLINE",

            "cpu": data["cpu"],

            "memory": data["memory"],

            "disk": data["disk"],

            "uptime": data["uptime"],

            "routes": routes,

            "ports": ports,

            "alerts": alerts

        })

    return render_template(

        "dashboard.html",

        data=output,

        cpu_history=cpu_history,

        mem_history=mem_history,

        device_count=device_count,

        last_updated=last_updated

    )


app.run(debug=True)
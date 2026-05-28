import paramiko


def collect_metrics(host, port, user, password):

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    try:

        ssh.connect(
            host,
            port=port,
            username=user,
            password=password,
            timeout=5
        )

    except Exception:

        return {
            "status": "OFFLINE",
            "cpu": "0",
            "memory": "0",
            "disk": "0%",
            "uptime": "Device unreachable",
            "routes": "No routes",
            "ports": "No open ports"
        }

    commands = {

        "cpu":
        "top -bn1 | grep Cpu | awk '{print $2+$4}'",

        "memory":
        "free | awk '/Mem/ {print $3/$2 *100.0}'",

        "disk":
        "df -h / | awk 'NR==2 {print $5}'",

        "uptime":
        "uptime -p",

        "routes":
        "ip route",

        "ports":
        "ss -tuln"

    }

    result = {}

    for name, cmd in commands.items():

        stdin, stdout, stderr = ssh.exec_command(cmd)

        result[name] = stdout.read().decode().strip()

    result["status"] = "ONLINE"

    ssh.close()

    return result
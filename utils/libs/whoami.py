from .system import *

class Whoami:
    def __init__(self):
        self.hostname=getHostname()
        self.current_user=getCurrentUser()
        self.current_dir=getCurrentDir()
        self.ip=getIp()
        self.dns=getUnixDnsIps()
        self.env=getEnv()

    def addAttribute(self, name, value):
        setattr(self, name, value)

    def getEnvVar(self, name) -> str:
        try:
            return self.env[name]
        except KeyError:
            message = "Expected environment variable '{}' not set.".format(name)
            print(message)
            raise Exception(message)

    def asText(self, urls=["google.com"], show_env=True, show_plain_secrets=True):
        result = "------------------------- WHOAMI -------------------------\n"
        result += "Hostname: %s\n" % self.hostname
        result += "Current user: %s\n" % self.current_user
        result += "Current dir: %s\n" % self.current_dir
        result += "IP: %s\n" % self.ip
        result += "DNSs: %s\n" % self.dns
        result += "Network test connection:\n"
        for url in urls:
            result += "\tWith %s: %s\n" % (url, str(testConnection(host=url)))
        if show_env:
            result += "App env variables:\n"
            for clave, valor in os.environ.items():
                if "APP" in clave:
                    if 'APP_SECRET_' in clave and not show_plain_secrets:
                        primeros_tres_caracteres = valor[:3]
                        valor = primeros_tres_caracteres + '*' * (len(valor) - 3)
                        result += ('\t%s = %s\n' % (clave, valor))
                    else:
                        result += ('\t%s = %s\n' % (clave, valor))    
        result += "------------------------- WHOAMI -------------------------"
        return result
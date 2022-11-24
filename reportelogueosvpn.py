import paramiko
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

class Ssh:
    def __init__(self):
        self.HOST = ''
        self.USERNAME = ''
        self.PASSWORD = ''

    def conecta(self):

        # Conectamos por ssh
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.load_system_host_keys()
        cliente.connect( hostname = self.HOST , username = self.USERNAME , password = self.PASSWORD )

        sftp = cliente.open_sftp()
        sftp.chdir('/var/log/')
        sftp.get('openvpn.log','openvpn.log')
        sftp.close()

        cliente.close()
    
    
    def enviar_mail(self, linea):

        today = (datetime.today()+timedelta(days=-1)).strftime('%d/%m/%Y')
        me = ''
        domain = ''
        me_domain = me + domain
        you =  '' #'vicky.figini@gmail.com'
        login = ''

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Reporte conexiones VPN - " + str(today)
        msg['From'] = me 
        msg['To'] = you

        html_mid = ''
        
        # Create the body of the message (a plain-text and an HTML version).
        text = " "

        for elemento in linea:
            cuenta = elemento
            cta = cuenta[0]
            ejecutivo = cuenta[1]
            html_mid += '\n' + """<tr>
            <td>"""+str(cta)+"""</td>
            <td>"""+str(ejecutivo)+"""</td>
            </tr>"""
            
        html = """\
        <head>
        <meta charset="utf-8" />
        </head>

        <body>
            <body>
            <p>Buen día, les enviamos la lista de conexiones por VPN del día de ayer: </p>
        <table border="1" cellpadding="0" cellspacing="0" padding: "3px" style="font-family:verdana" >
            <tr>
            <th style="background-color:lightpink">Hora</th>
            <th style="background-color:lightpink">EJECUTIVO</th>
            </tr>
        """ + html_mid + """
        </table>
        </html>
        </body>

        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        #part2 = MIMEText(html, 'html')
        part3 = MIMEText(html, 'html', 'utf-8')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        #msg.attach(part2)
        msg.attach(part3)

        # Send the message via local SMTP server.
        mail = smtplib.SMTP('webmail.internal.gesinco.com.ar:587')

        mail.ehlo()

        mail.starttls()

        mail.login(me, login)
        mail.sendmail(me_domain, you, msg.as_string())
        mail.quit()

    def procesar_log(self):
        today = float(datetime.today().strftime('%d'))

        #abrimos archivo
        try:
            entrada = 'openvpn.log'
            txt = open(entrada, 'r', encoding='utf-8', errors='ignore')
            conexiones = []
            names = []
            for line in txt:
                if int(line[4:6]) == int(today) - 1:
                
                    if line.find('Connection Initiated') != -1:
                        print(line)
                        #print('Establish')
                        hora = line[7:15]
                        bigin_name = line.find('[', 45)
                        end_name = line.find(']',bigin_name)
                        name = line[bigin_name+1:end_name]
                        #exclutions
                        if name != 'jalbarenque' and name not in names:
                            conexiones.append((hora, name))
                        names.append(name)
                       
            if conexiones:
                self.enviar_mail(conexiones)


        except Exception as error:
            print('Error al descargar archivo' + str(error))
            if conexiones:
                self.enviar_mail(conexiones)




if __name__ == '__main__':
    ssh = Ssh()
    ssh.conecta()
    ssh.procesar_log()


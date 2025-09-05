import paramiko


class SSH(object):
    """ ssh远程连接 """
    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

    def shell_cmd(self, cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.username, self.password, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            content = stdout.read().decode('utf-8')
            res = content.strip('\n')
            ssh.close()
            return res
        except Exception as e:
            print('ssh连接失败', e)
            return False
        
    def shell_upload(self, local_path, remote_path):    
        try:
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(local_path, remote_path)
            transport.close()
            print(f'文件上传成功, 上传路径为：{remote_path}')
            return True
        except Exception as e:
            print(f'文件上传失败, 错误信息为：{e}')
            return False
        
    def shell_download(self, remote_path, local_path):
        try:
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(remote_path, local_path)
            transport.close()
            print(f'文件下载成功, 下载路径为：{local_path}')
            return True
        except Exception as e:
            print(f'文件下载失败, 错误信息为：{e}')
            return False
        
    
    
    
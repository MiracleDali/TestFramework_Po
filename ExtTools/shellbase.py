import paramiko


class SSH(object):
    """ ssh远程连接 """
    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

    def shell_cmd(self, cmd):
        """
        连接远程服务器，并执行命令
        """
        try:
            ssh = paramiko.SSHClient()   # 创建 sshclient 对象，用于连接远程服务器

            # 设置了自动添加未知主机密钥的策略（AutoAddPolicy），避免首次连接时抛出异常。
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.username, self.password, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(cmd)

            # 读取并解码输出内容。
            content = stdout.read().decode('utf-8')

            # 去掉末尾的换行符后返回结果
            res = content.strip('\n')
            ssh.close()
            return res
        except Exception as e:
            print('ssh连接失败', e)
            return False
        
    def shell_upload(self, local_path, remote_path):    
        """
        连接远程服务器，上传文件
        """
        try:
            # 使用 Transport 建立底层 SSH 传输通道
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)

            # 通过 SFTPClient.from_transport 创建 SFTP 客户端。
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(local_path, remote_path)
            transport.close()
            print(f'文件上传成功, 上传路径为：{remote_path}')
            return True
        except Exception as e:
            print(f'文件上传失败, 错误信息为：{e}')
            return False
        
    def shell_download(self, remote_path, local_path):
        """
        连接远程服务器，下载文件
        """
        try:
            # 使用 Transport 建立底层 SSH 传输通道
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)

            # 通过 SFTPClient.from_transport 创建 SFTP 客户端。
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(remote_path, local_path)
            transport.close()
            print(f'文件下载成功, 下载路径为：{local_path}')
            return True
        except Exception as e:
            print(f'文件下载失败, 错误信息为：{e}')
            return False
        
    
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子铭牌邮件服务模块
负责电子铭牌生成后的文件压缩和邮件发送功能
"""
import os
import smtplib
import socket
import time
import traceback
from datetime import datetime
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.env import EmailConfig

import py7zr

# 设置SMTP超时时间（秒）
SMTP_TIMEOUT = 30
# 设置SMTP调试级别（0-4，4为最详细）
SMTP_DEBUG_LEVEL = 1
# 设置连接重试次数
MAX_RETRIES = 2


class NvmEmailUtil:
    """
    邮件发送
    """

    @classmethod
    def send_completion_email(cls, file_dir, email_address):
        """
        压缩生成的目录并发送邮件
        file_dir: 要压缩的目录路径
        email_address: 收件人邮箱地址
        """
        try:
            # 生成7z压缩文件路径
            dir_name = os.path.basename(file_dir)
            parent_dir = os.path.dirname(file_dir)
            zip_file_path = os.path.join(parent_dir, f"{dir_name}.7z")
            print(f"压缩文件路径: {zip_file_path}")

            # 检查目录是否存在
            if not os.path.exists(file_dir):
                print(f"错误: 目录 {file_dir} 不存在")
                return False
            print(f"找到目录: {file_dir}")

            # 压缩目录
            try:
                with py7zr.SevenZipFile(zip_file_path, 'w') as z:
                    z.writeall(file_dir, dir_name)
                print(f"目录已压缩为: {zip_file_path}")
            except Exception as e:
                print(f"压缩目录失败: {str(e)}")
                print(f"错误类型: {type(e).__name__}")
                traceback.print_exc()
                return False

            # 从配置文件读取邮件设置
            try:
                sender = EmailConfig.get('EMAIL_SENDER', 'your_email@example.com')
                password = EmailConfig.get('EMAIL_PASSWORD', 'your_email_password')
                smtp_server = EmailConfig.get('SMTP_SERVER', 'smtp.example.com')
                smtp_port = EmailConfig.get('SMTP_PORT', 587)

                # 验证配置是否完整
                if not all([sender, password, smtp_server, smtp_port]):
                    print("错误: 邮件配置不完整，请检查config.yaml")
                    print(
                        f"当前配置: sender={sender}, password={password}, smtp_server={smtp_server}, smtp_port={smtp_port}")
                    return False
                print(f"邮件配置已加载: sender={sender}, smtp_server={smtp_server}, smtp_port={smtp_port}")
            except Exception as e:
                print(f"读取配置文件失败: {str(e)}")
                print(f"错误类型: {type(e).__name__}")
                traceback.print_exc()
                return False

            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = Header(sender)
            msg['To'] = Header(email_address)
            msg['Subject'] = Header(f"电子铭牌文件 - {dir_name}", 'utf-8')

            # 邮件正文
            body = f"您好，\n\n您的电子铭牌文件已生成并压缩，请查收附件。\n\n目录名称: {dir_name}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n此致\n电子铭牌系统"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # 添加附件
            with open(zip_file_path, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(zip_file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(zip_file_path)}"'
                msg.attach(part)

            # 发送邮件
            print(f"准备连接到SMTP服务器: {smtp_server}:{smtp_port}")

            # 检查网络连接
            print(f"开始网络连接测试: {smtp_server}:{smtp_port}")
            if not cls.check_network_connectivity(smtp_server, smtp_port):
                print("网络连接测试失败，无法继续发送邮件")
                return False

            retry_count = 0
            server = None

            while retry_count <= MAX_RETRIES:
                try:
                    # 连接SMTP服务器
                    print(f"连接到SMTP服务器 (尝试 {retry_count + 1}/{MAX_RETRIES + 1}): {smtp_server}:{smtp_port}")
                    print(f"超时设置: {SMTP_TIMEOUT}秒")

                    if smtp_port == 465:
                        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
                        print("使用SMTP_SSL连接成功")
                    else:
                        server = smtplib.SMTP(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
                        print("使用SMTP连接成功")
                        print("启动TLS...")
                        server.starttls()
                        print("TLS启动成功")

                    # 设置调试级别
                    server.set_debuglevel(SMTP_DEBUG_LEVEL)
                    print(f"设置SMTP调试级别: {SMTP_DEBUG_LEVEL}")

                    break  # 连接成功，跳出重试循环
                except (socket.timeout, smtplib.SMTPConnectError) as e:
                    retry_count += 1
                    print(f"连接失败 (尝试 {retry_count}/{MAX_RETRIES + 1}): {str(e)}")
                    if retry_count > MAX_RETRIES:
                        print(f"达到最大重试次数 ({MAX_RETRIES})，连接失败")
                        return False
                    print(f"5秒后重试...")
                    time.sleep(5)

            if server is None:
                print("无法创建SMTP服务器连接")
                return False

            print(f"准备登录邮箱: {sender}")
            try:
                server.login(sender, password)
                print("邮箱登录成功")
            except smtplib.SMTPAuthenticationError:
                print("认证失败: 请检查用户名和密码是否正确")
                print(f"用户名: {sender}")
                return False
            except Exception as e:
                print(f"登录失败: {str(e)}")
                traceback.print_exc()
                return False

            print(f"准备发送邮件至: {email_address}")
            try:
                # 打印邮件信息（不包含附件）
                print(f"邮件主题: {msg['Subject']}")
                print(f"发件人: {msg['From']}")
                print(f"收件人: {msg['To']}")

                server.send_message(msg)
                print("邮件发送成功")
            except Exception as e:
                print(f"发送邮件失败: {str(e)}")
                traceback.print_exc()
                return False

            try:
                server.quit()
                print("SMTP服务器连接已关闭")
            except Exception as e:
                print(f"关闭服务器连接时出错: {str(e)}")

            print(f"邮件已发送至: {email_address}")
            return True
        except Exception as e:
            print(f"发送邮件时发生未预期错误: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            traceback.print_exc()
            return False

    @classmethod
    def check_network_connectivity(cls, host, port, timeout=5):
        """检查网络连接"""
        try:
            # 尝试连接到服务器
            with socket.create_connection((host, port), timeout=timeout) as s:
                print(f"网络连接测试成功: {host}:{port}")
                return True
        except (socket.timeout, socket.error) as e:
            print(f"网络连接测试失败: {host}:{port}, 错误: {str(e)}")
            return False


# 示例用法
if __name__ == '__main__':
    # 测试邮件发送功能
    test_dir = 'test_dir'
    test_email = 'test@example.com'
    NvmEmailService.send_completion_email(test_dir, test_email)

#!/usr/bin/env python3
"""
飞书 API 封装
支持：多维表格读写、图片上传下载
"""

import json
import os
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional


class FeishuClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化飞书客户端"""
        self.config = self._load_config(config_path)
        self.app_id = self.config["feishu"]["app_id"]
        self.app_secret = self.config["feishu"]["app_secret"]
        self.access_token = None
        self._get_access_token()
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        # 支持绝对路径和相对路径
        if not os.path.isabs(config_path):
            # 相对于脚本所在目录
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / config_path
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_access_token(self):
        """获取 access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        resp = requests.post(url, headers=headers, json=data)
        result = resp.json()
        if result.get("code") == 0:
            # 新版飞书 API 返回格式
            self.access_token = result.get("tenant_access_token") or result.get("data", {}).get("access_token")
        else:
            raise Exception(f"获取 access_token 失败: {result}")
    
    def _request(self, method: str, url: str, **kwargs) -> Dict:
        """发送请求"""
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Content-Type"] = "application/json; charset=utf-8"
        
        resp = requests.request(method, url, headers=headers, **kwargs)
        result = resp.json()
        
        if result.get("code") != 0:
            raise Exception(f"API 请求失败: {result}")
        return result.get("data", {})
    
    # ===== 多维表格操作 =====
    
    def get_table_records(self, table_id: str, filter_conditions: str = None) -> List[Dict]:
        """获取多维表格记录"""
        app_token = self.config["feishu"].get("app_token", "")
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        params = {"page_size": 100}
        if filter_conditions:
            params["filter"] = filter_conditions
        
        return self._request("GET", url, params=params).get("items", [])
    
    def create_table_record(self, table_id: str, fields: Dict) -> Dict:
        """创建多维表格记录"""
        app_token = self.config["feishu"].get("app_token", "")
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        data = {"fields": fields}
        return self._request("POST", url, json=data)
    
    def update_table_record(self, table_id: str, record_id: str, fields: Dict) -> Dict:
        """更新多维表格记录"""
        app_token = self.config["feishu"].get("app_token", "")
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        data = {"fields": fields}
        return self._request("PUT", url, json=data)
    
    # ===== 云空间文件操作 =====
    
    def upload_image(self, file_path: str, parent_node: str = None, for_bitable_attachment: bool = False) -> str:
        """上传图片到飞书
        
        Args:
            file_path: 图片文件路径
            parent_node: 云空间目录节点ID
            for_bitable_attachment: 是否用于多维表格附件字段（强制用drive API返回file_token）
        Returns:
            file_token: 用于写入多维表格附件字段
        """
        import os
        import uuid
        
        # 读取文件
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # 方法1: 用 image/v4/upload (返回 image_key，可用于图片字段)
        # 仅在不强制用 drive API 时尝试
        if not for_bitable_attachment:
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                files = {
                    'file': (file_name, open(file_path, 'rb'), 'image/png')
                }
                data = {
                    "image_type": "message",
                    "parent_type": "bitable",
                    "parent_id": "upload",
                    "size": str(file_size)
                }
                
                url = "https://open.feishu.cn/open-apis/image/v4/upload/"
                resp = requests.post(url, files=files, data=data, headers=headers)
                result = resp.json()
                
                if result.get("code") == 0:
                    return result["data"]["image_key"]
            except Exception as e:
                print(f"image API 失败: {e}")
        
        # 方法2: 用 drive/v1/files/upload_all (云空间/多维表格)
        # for_bitable_attachment=True 时用 bitable 类型上传，返回 file_token
        print("尝试 drive API...")
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        boundary = "----WebKitFormBoundary" + str(uuid.uuid4()).replace("-", "")[:16]
        
        body = f"--{boundary}\r\n"
        body += 'Content-Disposition: form-data; name="file_name"\r\n\r\n'
        body += f"{file_name}\r\n"
        
        body += f"--{boundary}\r\n"
        body += 'Content-Disposition: form-data; name="parent_type"\r\n\r\n'
        
        # 关键：用于多维表格附件时用 bitable，否则用 explorer
        if for_bitable_attachment:
            body += "bitable\r\n"
        else:
            body += "explorer\r\n"
        
        body += f"--{boundary}\r\n"
        body += 'Content-Disposition: form-data; name="parent_node"\r\n\r\n'
        
        # 关键：用于多维表格附件时用 app_token，否则用 parent_node
        if for_bitable_attachment:
            body += f"{self.config['feishu'].get('app_token', '')}\r\n"
        else:
            body += f"{parent_node or 'nodcnzQ6KyqOwfj6O10mhSE4tbf'}\r\n"
        
        body += f"--{boundary}\r\n"
        body += 'Content-Disposition: form-data; name="size"\r\n\r\n'
        body += f"{file_size}\r\n"
        
        body += f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
        body += "Content-Type: image/png\r\n\r\n"
        body = body.encode() + file_content + f"\r\n--{boundary}--\r\n".encode()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
        
        url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
        resp = requests.post(url, data=body, headers=headers)
        result = resp.json()
        
        if result.get("code") == 0:
            return result["data"]["file_token"]
        else:
            raise Exception(f"上传失败: {result}")
    
    def upload_images_to_record(self, table_id: str, record_id: str, 
                                 cover_image: str = None, 
                                 content_images: list = None) -> Dict:
        """上传图片到多维表格记录的封面图和内容图字段
        
        Args:
            table_id: 表格ID
            record_id: 记录ID
            cover_image: 封面图文件路径
            content_images: 内容图文件路径列表
        
        Returns:
            更新结果
        """
        fields = {}
        
        # 上传封面图
        if cover_image:
            print(f"📤 上传封面图: {cover_image}")
            file_token = self.upload_image(cover_image, for_bitable_attachment=True)
            fields["封面图"] = [{"file_token": file_token}]
            print(f"   ✅ {file_token}")
        
        # 上传内容图（多张，按顺序）
        if content_images:
            print(f"📤 上传{len(content_images)}张内容图...")
            content_tokens = []
            for i, img_path in enumerate(content_images, 1):
                print(f"   [{i}/{len(content_images)}] {img_path}")
                file_token = self.upload_image(img_path, for_bitable_attachment=True)
                content_tokens.append({"file_token": file_token})
                print(f"   ✅ {file_token}")
            fields["内容图"] = content_tokens
        
        if not fields:
            print("⚠️ 没有图片需要上传")
            return {}
        
        # 更新记录
        print(f"📝 更新记录 {record_id}...")
        result = self.update_table_record(table_id, record_id, fields)
        print(f"✅ 更新完成")
        return result
    
    def get_download_url(self, file_token: str) -> str:
        """获取文件下载链接"""
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download_url"
        data = self._request("GET", url)
        return data.get("download_url", "")
    
    def download_file(self, file_token: str, save_path: str):
        """下载文件"""
        url = self.get_download_url(file_token)
        if not url:
            raise Exception("无法获取下载链接")
        
        resp = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(resp.content)


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """加载配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    # 测试
    client = FeishuClient()
    print("✅ 飞书客户端初始化成功")
    print(f"App ID: {client.app_id}")

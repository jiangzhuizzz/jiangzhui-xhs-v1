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
    
    def upload_image(self, file_path: str, token: str = None) -> str:
        """上传图片到飞书云空间"""
        url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        file_name = os.path.basename(file_path)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # 构建 multipart 请求
        files = {
            'file': (file_name, file_content, 'image/png')
        }
        data = {
            'parent_node': token or "root",
            'file_name': file_name
        }
        
        resp = requests.post(url, headers=headers, files=files, data=data)
        result = resp.json()
        
        if result.get("code") == 0:
            return result["data"]["file"]["token"]
        else:
            raise Exception(f"上传图片失败: {result}")
    
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

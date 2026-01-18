# -*- coding: utf-8 -*-
"""
配置校验脚本 (V6.1 新增)
========================
在执行数据采集前校验 config.json 的完整性
"""

import json, sys, os
from typing import Dict, List, Optional


class ConfigValidator:
    """配置校验器"""
    
    # 必需字段
    REQUIRED_FIELDS = ['wechat_push_token']
    
    # 推荐的模式配置
    RECOMMENDED_LITE_MODE = {
        'keywords': ['理财', '基金', '股票', '黄金', '存钱'],
        'min_likes': 500,
        'max_fans': 20000
    }
    
    RECOMMENDED_PRO_MODE = {
        'keywords': ['理财', '基金', '股票', '副业', '搞钱', '存钱', '宏观经济', '黄金', 'A股', '保险'],
        'min_likes': 1000,
        'max_fans': 20000
    }
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_encoding(self) -> bool:
        """校验文件编码"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                f.read()
            return True
        except UnicodeDecodeError as e:
            self.errors.append(f"编码错误: 文件不是有效的UTF-8编码 ({e})")
            return False
    
    def load_config(self) -> bool:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            self.errors.append(f"配置文件不存在: {self.config_path}")
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON解析错误: {e}")
            return False
    
    def validate_required_fields(self) -> bool:
        """校验必需字段"""
        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                self.errors.append(f"缺少必需字段: {field}")
                return False
            
            value = self.config[field]
            if not value or not str(value).strip():
                self.errors.append(f"字段 {field} 不能为空")
                return False
        
        return True
    
    def validate_token_format(self) -> bool:
        """校验token格式"""
        token = self.config.get('wechat_push_token', '')
        if len(token) < 10:
            self.warnings.append("wechat_push_token 长度较短,可能不正确")
        return True
    
    def validate_mode_config(self, mode: str) -> bool:
        """校验指定模式的配置"""
        mode_key = 'lite_mode' if mode == 'lite' else 'finance_pro_mode'
        
        if mode_key not in self.config:
            self.errors.append(f"缺少模式配置: {mode_key}")
            return False
        
        mode_config = self.config[mode_key]
        
        if 'keywords' not in mode_config:
            self.errors.append(f"模式 {mode} 缺少 keywords 配置")
            return False
        
        if not isinstance(mode_config['keywords'], list) or len(mode_config['keywords']) == 0:
            self.errors.append(f"模式 {mode} 的 keywords 必须是非空数组")
            return False
        
        # 校验关键词数量
        expected_count = 5 if mode == 'lite' else 10
        if len(mode_config['keywords']) != expected_count:
            self.warnings.append(f"模式 {mode} 的关键词数量应为 {expected_count},当前为 {len(mode_config['keywords'])}")
        
        return True
    
    def validate_exclude_keywords(self) -> bool:
        """校验排除关键词配置"""
        if 'exclude_keywords' not in self.config:
            self.warnings.append("建议配置 exclude_keywords 以过滤非财经内容")
            return True
        
        exclude = self.config['exclude_keywords']
        if not isinstance(exclude, list):
            self.errors.append("exclude_keywords 必须是数组")
            return False
        
        return True
    
    def validate(self, mode: Optional[str] = None) -> Dict:
        """执行完整校验"""
        print("=" * 60)
        print("配置校验 (V6.1)")
        print("=" * 60)
        
        # 1. 编码校验
        print("  校验编码...")
        if not self.validate_encoding():
            self._print_result()
            return self._build_result()
        
        # 2. 加载配置
        print("  加载配置...")
        if not self.load_config():
            self._print_result()
            return self._build_result()
        
        print(f"  配置已加载")
        
        # 3. 必需字段
        print("  校验必需字段...")
        self.validate_required_fields()
        
        # 4. Token格式
        print("  校验Token格式...")
        self.validate_token_format()
        
        # 5. 模式配置
        if mode:
            print(f"  校验 {mode} 模式配置...")
            self.validate_mode_config(mode)
        
        # 6. 排除关键词
        print("  校验排除关键词...")
        self.validate_exclude_keywords()
        
        self._print_result()
        return self._build_result()
    
    def _print_result(self):
        """打印校验结果"""
        print("-" * 60)
        if self.errors:
            for error in self.errors:
                print(f"  ❌ {error}")
        if self.warnings:
            for warning in self.warnings:
                print(f"  ⚠️ {warning}")
        if not self.errors and not self.warnings:
            print("  ✅ 所有校验通过")
        print("=" * 60)
    
    def _build_result(self) -> Dict:
        return {
            'status': 'error' if self.errors else ('warning' if self.warnings else 'success'),
            'errors': self.errors,
            'warnings': self.warnings,
            'config': self.config
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='校验配置文件')
    parser.add_argument('--config', default='../config.json', help='配置文件路径')
    parser.add_argument('--mode', choices=['lite', 'pro'], help='校验指定模式')
    args = parser.parse_args()
    
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    validator = ConfigValidator(config_path)
    result = validator.validate(args.mode)
    
    # 返回退出码
    if result['status'] == 'error':
        sys.exit(1)
    elif result['status'] == 'warning' and args.mode:
        sys.exit(0)  # 警告不阻止执行
    sys.exit(0)


if __name__ == '__main__':
    main()

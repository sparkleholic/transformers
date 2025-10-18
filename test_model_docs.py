#!/usr/bin/env python3
"""
통합된 문서 생성기 테스트 스크립트

생성된 모듈들이 실제로 import 되는지 테스트합니다.
"""

import yaml
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
CONFIG_FILE = PROJECT_ROOT / "generate_model_docs.yaml"


def discover_core_modules():
    """src/transformers 디렉토리에서 핵심 모듈들을 자동 탐지합니다."""
    transformers_dir = PROJECT_ROOT / "src" / "transformers"
    skip_items = {
        'models', '__pycache__', 'tests', 'test_*', 'deprecated',
        '__init__.py', '*.pyc', '*.pyo', '.git'
    }
    
    core_modules = []
    
    if not transformers_dir.exists():
        return []
    
    for item in transformers_dir.iterdir():
        if item.name.startswith('.') or item.name.startswith('__'):
            continue
            
        # 스킵할 항목들 확인
        if any(item.name == skip or item.name.startswith(skip.rstrip('*')) 
               for skip in skip_items):
            continue
            
        # Python 모듈 파일인지 확인
        if item.is_file() and item.suffix == '.py':
            module_name = item.stem
            if module_name != '__init__':
                core_modules.append(module_name)
    
    return sorted(core_modules)


def test_core_modules():
    """Core 모듈들의 import 테스트"""
    print("🔧 Testing Core Modules...")
    
    core_modules = discover_core_modules()
    success_count = 0
    
    for module in core_modules:
        try:
            exec(f"from transformers import {module}")
            print(f"✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module}: {e}")
        except Exception as e:
            print(f"⚠️ {module}: {e}")
    
    print(f"📊 Core modules: {success_count}/{len(core_modules)} successful")
    return success_count, len(core_modules)


def test_model_packages():
    """Model 패키지들의 import 테스트"""
    print("\n📦 Testing Model Packages...")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    models = config.get('priority_models', [])
    success_count = 0
    
    for model in models:
        try:
            exec(f"from transformers.models import {model}")
            print(f"✅ {model}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {model}: {e}")
        except Exception as e:
            print(f"⚠️ {model}: {e}")
    
    print(f"📊 Model packages: {success_count}/{len(models)} successful")
    return success_count, len(models)


def discover_model_submodules(model_name):
    """특정 모델 디렉토리에서 서브모듈들을 자동 탐지합니다."""
    models_dir = PROJECT_ROOT / "src" / "transformers" / "models"
    model_dir = models_dir / model_name
    skip_items = {'__pycache__', 'tests', 'test_*', '__init__.py'}
    
    if not model_dir.exists() or not model_dir.is_dir():
        return []
    
    submodules = []
    
    for item in model_dir.iterdir():
        if item.name.startswith('.') or item.name.startswith('__'):
            continue
            
        # 스킵할 항목들 확인
        if any(item.name == skip or item.name.startswith(skip.rstrip('*')) 
               for skip in skip_items):
            continue
            
        # Python 모듈 파일인지 확인
        if item.is_file() and item.suffix == '.py':
            module_name = item.stem
            if module_name != '__init__':
                submodules.append(module_name)
    
    return sorted(submodules)


def test_model_submodules():
    """Model 서브모듈들의 import 테스트"""
    print("\n🔍 Testing Model Submodules...")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    models_list = config.get('priority_models', [])
    total_submodules = 0
    success_count = 0
    
    for model_name in models_list:
        submodules = discover_model_submodules(model_name)
        
        if not submodules:
            print(f"\n📝 Testing {model_name}: No submodules found")
            continue
            
        print(f"\n📝 Testing {model_name}...")
        
        for submodule in submodules:
            total_submodules += 1
            try:
                module_path = f"transformers.models.{model_name}"
                exec(f"from {module_path} import {submodule}")
                print(f"  ✅ {submodule}")
                success_count += 1
            except ImportError as e:
                print(f"  ❌ {submodule}: {e}")
            except Exception as e:
                print(f"  ⚠️ {submodule}: {e}")
    
    submodule_stats = f"{success_count}/{total_submodules}"
    print(f"\n📊 Model submodules: {submodule_stats} successful")
    return success_count, total_submodules


def main():
    print("🧪 Testing Generated Documentation Modules")
    print("=" * 50)
    
    # 각 카테고리 테스트
    core_stats = test_core_modules()
    package_stats = test_model_packages()
    submodule_stats = test_model_submodules()
    
    # 최종 결과
    total_success = core_stats[0] + package_stats[0] + submodule_stats[0]
    total_modules = core_stats[1] + package_stats[1] + submodule_stats[1]
    
    print("\n" + "=" * 50)
    print("📊 Final Test Results")
    print("=" * 50)
    print(f"Core Modules: {core_stats[0]}/{core_stats[1]}")
    print(f"Model Packages: {package_stats[0]}/{package_stats[1]}")
    print(f"Model Submodules: {submodule_stats[0]}/{submodule_stats[1]}")
    print(f"Total: {total_success}/{total_modules}")
    print(f"Success Rate: {total_success/total_modules*100:.1f}%")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Python 3.8 타입 힌트 호환성 수정 스크립트

Python 3.10+ 문법을 Python 3.8 호환 문법으로 변환합니다:
- str | None -> Optional[str]
- list[str] -> List[str]
- dict[str, ...] -> Dict[str, ...]
- tuple[...] -> Tuple[...]
"""

import re
import sys
from pathlib import Path

# 변환 패턴
REPLACEMENTS = [
    # Union 타입 (str | None, int | None 등)
    (r'(\w+)\s*\|\s*None', r'Optional[\1]'),
    (r'(\w+)\s*\|\s*(\w+)', r'Union[\1, \2]'),
    
    # Generic 타입 (list[str], dict[str, int] 등)
    (r'list\[', r'List['),
    (r'dict\[', r'Dict['),
    (r'tuple\[', r'Tuple['),
    (r'set\[', r'Set['),
]

def fix_file(file_path: Path) -> bool:
    """파일의 타입 힌트를 Python 3.8 호환으로 수정"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # typing import 확인 및 추가
        needs_optional = 'Optional' in content and 'from typing import' in content
        needs_union = 'Union' in content and 'from typing import' in content
        needs_list = 'List[' in content and 'from typing import' in content
        needs_dict = 'Dict[' in content and 'from typing import' in content
        needs_tuple = 'Tuple[' in content and 'from typing import' in content
        
        # 타입 힌트 변환
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # typing import 추가
        if 'from typing import' in content:
            # 기존 import 라인 찾기
            import_match = re.search(r'from typing import ([^\n]+)', content)
            if import_match:
                imports = import_match.group(1).split(',')
                imports = [imp.strip() for imp in imports]
                
                # 필요한 타입 추가
                if 'Optional' not in imports and 'Optional' in content:
                    imports.append('Optional')
                if 'Union' not in imports and 'Union' in content:
                    imports.append('Union')
                if 'List' not in imports and 'List[' in content:
                    imports.append('List')
                if 'Dict' not in imports and 'Dict[' in content:
                    imports.append('Dict')
                if 'Tuple' not in imports and 'Tuple[' in content:
                    imports.append('Tuple')
                
                # 중복 제거 및 정렬
                imports = sorted(set(imports))
                new_import = f"from typing import {', '.join(imports)}"
                content = re.sub(r'from typing import [^\n]+', new_import, content)
        else:
            # typing import가 없으면 추가
            imports = []
            if 'Optional' in content:
                imports.append('Optional')
            if 'Union' in content:
                imports.append('Union')
            if 'List[' in content:
                imports.append('List')
            if 'Dict[' in content:
                imports.append('Dict')
            if 'Tuple[' in content:
                imports.append('Tuple')
            
            if imports:
                # 파일 상단에 import 추가 (다른 import 다음에)
                import_pattern = r'(from \w+ import [^\n]+\n)'
                match = re.search(import_pattern, content)
                if match:
                    pos = match.end()
                    new_import = f"from typing import {', '.join(sorted(set(imports)))}\n"
                    content = content[:pos] + new_import + content[pos:]
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """메인 함수"""
    backend_dir = Path(__file__).parent.parent / 'app'
    
    if not backend_dir.exists():
        print(f"Error: {backend_dir} not found", file=sys.stderr)
        sys.exit(1)
    
    fixed_count = 0
    for py_file in backend_dir.rglob('*.py'):
        if fix_file(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()


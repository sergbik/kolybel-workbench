import os
import sys
import shutil

def get_indent(line):
    if not line.strip(): return 999 
    return len(line) - len(line.lstrip())

def assemble_patch(original_path, output_path, patches, version_update=None):
    if not os.path.exists(original_path):
        print(f"ERROR: Original not found: {original_path}")
        return False
    with open(original_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    final_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched = False
        if version_update and version_update['old'] in line:
            final_lines.append(line.replace(version_update['old'], version_update['new']))
            i += 1
            continue
        for signature, new_block in patches.items():
            if signature in line:
                final_lines.extend(new_block)
                start_indent = get_indent(line)
                i += 1
                while i < len(lines):
                    if lines[i].strip() and get_indent(lines[i]) <= start_indent:
                        break
                    i += 1
                matched = True
                break
        if not matched:
            final_lines.append(line)
            i += 1
    final_text = "".join(final_lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    return True

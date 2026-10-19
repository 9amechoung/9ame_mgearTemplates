# -*- coding: utf-8 -*-
"""Maya 스크립트 에디터(Python)에서 실행: .pkr 의 컨트롤이 씬에 있는지 검사한다.

    PKR_PATH = r"D:/path/to/biped_anim_picker.pkr"
    NAMESPACE = ""            # 리퍼런스 리그면 "char01" 처럼 입력
    exec(open(r"D:/path/to/check_picker_controls.py").read())

없는 컨트롤은 피커에서 클릭해도 아무것도 선택되지 않으므로,
리그 이름에 맞게 build_biped_picker.py 를 수정하고 다시 생성하면 된다.
"""

import json

import maya.cmds as cmds


def check_picker_controls(pkr_path, namespace=""):
    with open(pkr_path, "r") as f:
        data = json.load(f)

    missing = {}
    total = set()
    for tab in data.get("tabs", []):
        for item in tab.get("data", {}).get("items", []):
            for ctl in item.get("controls", []):
                total.add(ctl)
                node = "{}:{}".format(namespace, ctl) if namespace else ctl
                if not cmds.objExists(node):
                    missing.setdefault(tab.get("name"), set()).add(node)

    count = sum(len(v) for v in missing.values())
    print("-" * 60)
    print("Picker : {}".format(pkr_path))
    print("Found  : {} / {} controls".format(len(total) - count, len(total)))
    for tab_name, nodes in sorted(missing.items()):
        print("[{}] missing {}:".format(tab_name, len(nodes)))
        for node in sorted(nodes):
            print("    " + node)
    print("-" * 60)
    return missing


if __name__ == "__main__":
    check_picker_controls(PKR_PATH, globals().get("NAMESPACE", ""))  # noqa: F821

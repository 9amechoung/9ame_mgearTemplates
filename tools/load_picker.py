# -*- coding: utf-8 -*-
"""Maya 스크립트 에디터(Python)에서 실행: .pkr 을 씬의 피커 노드로 불러오고 피커 창을 연다.

    PKR_PATH = r"D:/path/to/biped_anim_picker.pkr"
    exec(open(r"D:/path/to/load_picker.py").read())

File > Open / Import 나 드래그&드롭으로 .pkr 을 열면 Maya 가
"No translator found" 에러를 낸다(.pkr 은 Maya 씬이 아니다).
이 스크립트는 Maya 파일 열기를 거치지 않고 mGear 피커 노드에 데이터를 직접 쓴다.
같은 이름의 피커 노드가 있으면 내용을 덮어쓴다.
"""

import json

import maya.cmds as cmds


def load_picker(pkr_path, node_name="PICKER_DATAS"):
    import mgear.anim_picker
    from mgear.anim_picker import picker_node

    with open(pkr_path, "r") as f:
        data = json.load(f)

    data_node = picker_node.DataNode(name=node_name)
    if not data_node.exists():
        data_node.create()
    data_node.set_data(data)
    data_node.write_data(to_node=True, to_file=False)

    cmds.select(clear=True)
    mgear.anim_picker.load()
    print("Picker loaded: {} -> {}".format(pkr_path, data_node.name))
    return data_node.name


if __name__ == "__main__":
    load_picker(PKR_PATH)  # noqa: F821

# -*- coding: utf-8 -*-
"""mGear Anim Picker 템플릿(.pkr) 생성기.

mGear 기본 Biped 가이드(biped template)로 빌드한 리그용 Anim Picker 파일을 만든다.
Maya 없이 일반 Python 3 로 실행한다.

    python tools/build_biped_picker.py

결과물:
    templates/biped_anim_picker.pkr      -> Anim Picker 에서 Load
    templates/biped_anim_picker_*.svg    -> 탭별 레이아웃 미리보기

좌표계는 Anim Picker 와 동일하게 Y-up 이다. 캐릭터의 L(왼쪽)은 화면 오른쪽(+X)에 둔다.
컨트롤 이름이 다른 리그라면 아래 이름 문자열만 바꾸고 다시 실행하면 된다.

섹션 패널은 Anim Picker 2.0 의 backdrop(둥근 패널 + 타이틀 바)을 쓴다.
이전 버전에서는 반투명 사각형으로 보이고 나머지 기능은 그대로 동작한다.
"""

from __future__ import print_function

import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "templates")
OUT_NAME = "biped_anim_picker"

# --------------------------------------------------------------------------
# 팔레트 (R, G, B, A)  -  mGear 관례: L=파랑, R=빨강, C=노랑
# FK 는 진한 색, IK 는 같은 계열의 밝은 색
# --------------------------------------------------------------------------
COLOR = {
    "C_fk": (255, 201, 74, 235),
    "C_ik": (255, 150, 70, 235),
    "L_fk": (61, 139, 255, 235),
    "L_ik": (120, 210, 255, 235),
    "R_fk": (255, 84, 96, 235),
    "R_ik": (255, 160, 170, 235),
    "root": (100, 214, 150, 235),
    "ui": (181, 140, 255, 240),
    "button": (59, 66, 82, 255),
    "primary": (94, 196, 164, 255),
    "danger": (191, 76, 84, 255),
    "panel": (120, 135, 160, 38),
    "panel_C": (255, 201, 74, 22),
    "panel_L": (61, 139, 255, 28),
    "panel_R": (255, 84, 96, 28),
}
WHITE = (240, 242, 245, 255)
DARK = (25, 28, 34, 255)
MUTED = (160, 168, 180, 255)
INVISIBLE = (0, 0, 0, 0)


# --------------------------------------------------------------------------
# 도형
# --------------------------------------------------------------------------
def _r(v):
    return round(v, 3)


def rounded_rect_handles(w, h, radius=None, seg=3):
    """둥근 모서리 사각형. radius 가 짧은 변의 절반이면 캡슐 모양."""
    hw, hh = w * 0.5, h * 0.5
    if radius is None:
        radius = min(w, h) * 0.3
    radius = min(radius, hw, hh)
    corners = [  # (중심 x, 중심 y, 시작 각도)  -  시계 방향
        (hw - radius, hh - radius, 90),
        (hw - radius, -hh + radius, 0),
        (-hw + radius, -hh + radius, -90),
        (-hw + radius, hh - radius, -180),
    ]
    pts = []
    for cx, cy, start in corners:
        for i in range(seg + 1):
            a = math.radians(start - 90.0 * i / seg)
            pts.append([_r(cx + radius * math.cos(a)),
                        _r(cy + radius * math.sin(a))])
    return pts


def circle_handles(r, count=16):
    return [[_r(r * math.cos(math.pi * 0.5 - 2 * math.pi * i / count)),
             _r(r * math.sin(math.pi * 0.5 - 2 * math.pi * i / count))]
            for i in range(count)]


def diamond_handles(r):
    return [[0, r], [r, 0], [0, -r], [-r, 0]]


def rect_handles(w, h):
    hw, hh = w * 0.5, h * 0.5
    return [[hw, hh], [hw, -hh], [-hw, -hh], [-hw, hh]]


# --------------------------------------------------------------------------
# 아이템
# --------------------------------------------------------------------------
def item(pos, handles, color, controls=None, text=None, text_size=None,
         text_color=None, script=None, menus=None):
    data = {
        "color": list(color),
        "position": [_r(pos[0]), _r(pos[1])],
        "handles": handles,
    }
    if controls:
        data["controls"] = list(controls)
    if text:
        data["text"] = text
        data["text_size"] = float(text_size or 9)
        data["text_color"] = list(text_color or DARK)
    if script:
        data["action_mode"] = True
        data["action_script"] = script
    if menus:
        data["menus"] = menus
    return data


def ctl(pos, w, h, color, controls, text=None, text_size=7, radius=None):
    """둥근 사각형 컨트롤."""
    return item(pos, rounded_rect_handles(w, h, radius), color, controls,
                text, text_size)


def ctl_circle(pos, r, color, controls):
    return item(pos, circle_handles(r), color, controls)


def ctl_diamond(pos, r, color, controls):
    return item(pos, diamond_handles(r), color, controls)


def label(text, pos, size=9, color=WHITE):
    # 투명한 2점짜리 아이템 = 텍스트 라벨 (mGear 기본 템플릿과 같은 방식)
    return item(pos, [[0.0, 0.0], [1.0, 0.0]], INVISIBLE,
                text=text, text_size=size, text_color=color)


def button(text, pos, script, w=80, h=22, color=COLOR["button"],
           text_color=WHITE, size=8, controls=None):
    data = item(pos, rounded_rect_handles(w, h, h * 0.5), color,
                controls=controls, text=text, text_size=size,
                text_color=text_color, script=script)
    return data


def panel(title, center, w, h, color=COLOR["panel"]):
    """Anim Picker 2.0 backdrop (둥근 패널 + 타이틀 바)."""
    data = item(center, rect_handles(w, h), color)
    data["backdrop"] = True
    data["title"] = title
    data["corner_radius"] = 10.0
    return data


# --------------------------------------------------------------------------
# 액션 스크립트
#   Anim Picker 가 제공하는 변수: __NAMESPACE__, __INIT__, __SELF__,
#   __CONTROLS__, __FLATCONTROLS__
#   __INIT__ 이 True 일 때(피커 로드 시)는 실행하지 않도록 가드한다.
# --------------------------------------------------------------------------
_NAMESPACE_FUNC = '''import maya.cmds as cmds


def _namespace():
    # 피커에 네임스페이스가 지정되지 않았으면 선택한 노드에서,
    # 그래도 없으면 씬에 컨트롤러 셋이 있는 네임스페이스가 하나뿐일 때 그것을 쓴다.
    if __NAMESPACE__:
        return __NAMESPACE__
    sel = cmds.ls(sl=True) or []
    if sel:
        return sel[0].split("|")[-1].rpartition(":")[0]
    if cmds.ls("*_controllers_grp", type="objectSet"):
        return ""
    found = sorted(set(
        s.rpartition(":")[0] for s in
        cmds.ls("*:*_controllers_grp", type="objectSet", recursive=True) or []))
    if len(found) == 1:
        return found[0]
    if len(found) > 1:
        cmds.warning("Anim Picker: several rigs found ({}). Pick the namespace "
                     "in the picker or select a control of the rig first."
                     .format(", ".join(found)))
    return ""
'''

_GET_ALL_CTLS = _NAMESPACE_FUNC + '''

def _ns(namespace, name):
    return "{}:{}".format(namespace, name) if namespace else name


def _flatten_set(node, seen):
    result = []
    for member in cmds.sets(node, q=True) or []:
        if cmds.nodeType(member) == "objectSet":
            if member not in seen:
                seen.add(member)
                result += _flatten_set(member, seen)
        else:
            result.append(member)
    return result


def _all_controls():
    # 1) mGear controller set: <rigName>_controllers_grp (sub-sets flattened)
    namespace = _namespace()
    sets = cmds.ls(_ns(namespace, "*_controllers_grp"), type="objectSet") or []
    ctls = []
    seen = set(sets)
    for s in sets:
        ctls += _flatten_set(s, seen)
    # 2) fallback: mGear controls carry an "isCtl" attribute
    if not ctls:
        ctls = cmds.ls(_ns(namespace, "*.isCtl"), objectsOnly=True) or []
    # 3) fallback: transforms named *_ctl
    if not ctls:
        ctls = cmds.ls(_ns(namespace, "*_ctl"), type="transform") or []
    if not ctls:
        cmds.warning("Anim Picker: no controls found in namespace '{}'"
                     .format(namespace))
    return list(dict.fromkeys(ctls))
'''

_RESET_FUNC = '''

def _reset(nodes):
    failed = []
    for node in nodes:
        for attr in cmds.listAttr(node, keyable=True, unlocked=True) or []:
            plug = "{}.{}".format(node, attr)
            try:
                default = cmds.attributeQuery(attr, node=node, listDefault=True)
                if default:
                    cmds.setAttr(plug, default[0])
            except Exception:
                failed.append(plug)
    if failed:
        cmds.warning("Anim Picker: could not reset {} attributes "
                     "(connected?): {}".format(len(failed), ", ".join(failed[:10])))
'''

SCRIPT_SELECT_ALL = _GET_ALL_CTLS + '''

if not __INIT__:
    cmds.select(_all_controls(), r=True)
'''

SCRIPT_KEY_ALL = _GET_ALL_CTLS + '''

if not __INIT__:
    ctls = _all_controls()
    if ctls:
        cmds.setKeyframe(ctls)
'''

SCRIPT_RESET_ALL = _GET_ALL_CTLS + _RESET_FUNC + '''

if not __INIT__:
    cmds.undoInfo(openChunk=True)
    try:
        _reset(_all_controls())
    finally:
        cmds.undoInfo(closeChunk=True)
'''

SCRIPT_RESET_SEL = '''import maya.cmds as cmds
''' + _RESET_FUNC + '''

if not __INIT__:
    cmds.undoInfo(openChunk=True)
    try:
        _reset(cmds.ls(sl=True) or [])
    finally:
        cmds.undoInfo(closeChunk=True)
'''

SCRIPT_KEY_SEL = '''import maya.cmds as cmds

if not __INIT__:
    sel = cmds.ls(sl=True)
    if sel:
        cmds.setKeyframe(sel)
'''

SCRIPT_KEY_ITEM_CONTROLS = '''import maya.cmds as cmds

if not __INIT__:
    ctls = [c for c in __FLATCONTROLS__ if cmds.objExists(c)]
    if ctls:
        cmds.setKeyframe(ctls)
'''


_MIRROR_FUNC = '''
import re

_SIDE = re.compile(r"_([LR])(\\d+)_")
_TRANSFORM = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
_SKIP = ("isRig", "uiHost", "_ctl")


def _other(node):
    swap = {"L": "R", "R": "L"}
    return _SIDE.sub(lambda m: "_{}{}_".format(swap[m.group(1)], m.group(2)),
                     node, count=1)


def _channels(node):
    # mGear 미러와 같은 채널: 트랜스폼 + 숫자형 유저 속성 (inv* 등 제외).
    # 반전 여부는 컨트롤의 inv<Attr> 속성(mGear 가 빌드 시 기록)을 따른다.
    user = cmds.listAttr(node, userDefined=True, keyable=True) or []
    result = []
    for attr in _TRANSFORM + tuple(user):
        if attr.startswith("inv") or any(k in attr for k in _SKIP):
            continue
        plug = "{}.{}".format(node, attr)
        try:
            value = cmds.getAttr(plug)
        except Exception:
            continue
        if isinstance(value, bool):
            value = int(value)
        if not isinstance(value, (int, float)):
            continue
        inv = "{}.inv{}".format(node, attr.lower().capitalize())
        if cmds.objExists(inv) and cmds.getAttr(inv):
            value = -value
        result.append((attr, value))
    return result


def _set(plug, value):
    # 키가 있는 속성은 현재 프레임에 키로 넣는다(mGear 미러는 키 있는
    # 속성을 건너뛰어서 키 작업 중에는 미러가 안 먹는다).
    if cmds.getAttr(plug, lock=True):
        return False
    sources = cmds.listConnections(plug, source=True, destination=False,
                                   skipConversionNodes=True) or []
    if sources:
        if all(cmds.nodeType(n).startswith("animCurve") for n in sources):
            cmds.setKeyframe(plug, value=value)
            return True
        return False
    cmds.setAttr(plug, value)
    return True


def _mirror(nodes, flip=False):
    if not nodes:
        cmds.warning("Anim Picker: nothing to mirror")
        return
    # 값을 모두 읽은 뒤에 쓴다 (Flip 시 양쪽이 서로의 원래 값을 받도록)
    entries = []
    nodes = [n for n in dict.fromkeys(nodes)
             if n.endswith("_ctl") or cmds.objExists(n + ".isCtl")]
    for node in nodes:
        target = _other(node)
        if not cmds.objExists(target):
            continue
        entries.append((target, _channels(node)))
        if flip and target != node and target not in nodes:
            entries.append((node, _channels(target)))
    failed = []
    cmds.undoInfo(openChunk=True)
    try:
        for target, channels in entries:
            for attr, value in channels:
                plug = "{}.{}".format(target, attr)
                if not cmds.objExists(plug):
                    continue
                try:
                    if not _set(plug, value):
                        failed.append(plug)
                except Exception:
                    failed.append(plug)
    finally:
        cmds.undoInfo(closeChunk=True)
    if failed:
        cmds.warning("Anim Picker: skipped {} locked/connected attributes: {}"
                     .format(len(failed), ", ".join(failed[:10])))


def _copy_side(side, parts):
    # side 쪽 컨트롤(parts 컴포넌트)의 포즈를 반대쪽에 복사한다.
    namespace = _namespace()
    pattern = "*_{}*_ctl".format(side)
    if namespace:
        pattern = "{}:{}".format(namespace, pattern)
    nodes = []
    for node in cmds.ls(pattern, type="transform") or []:
        short = node.split("|")[-1].split(":")[-1]
        match = _SIDE.search(short)
        if match and match.group(1) == side and short.split("_")[0] in parts:
            nodes.append(node)
    _mirror(nodes)
'''

LIMB_PARTS = ("arm", "armUI", "shoulder", "finger", "thumb", "thumbRoll",
              "meta", "leg", "legUI", "foot")
HAND_PARTS = ("finger", "thumb", "thumbRoll", "meta")


def script_copy_side(side, parts):
    """side(L/R) 의 팔·다리(또는 손) 포즈를 반대쪽에 복사."""
    return _NAMESPACE_FUNC + _MIRROR_FUNC + '''
if not __INIT__:
    _copy_side({!r}, {!r})
'''.format(side, parts)


SCRIPT_MIRROR_SEL = _NAMESPACE_FUNC + _MIRROR_FUNC + '''
if not __INIT__:
    _mirror(cmds.ls(sl=True) or [])
'''

SCRIPT_FLIP_SEL = _NAMESPACE_FUNC + _MIRROR_FUNC + '''
if not __INIT__:
    _mirror(cmds.ls(sl=True) or [], flip=True)
'''


def script_ikfk(limb, side):
    """mGear anim_utils 의 IK/FK 매칭 (클릭 시 현재 상태의 반대로 전환+매칭)."""
    ik_rot = (',\n        ik_rot="arm_{}_ikRot_ctl"'.format(side)
              if limb == "arm" else "")
    return _NAMESPACE_FUNC + '''
from mgear.core import anim_utils

if not __INIT__:
    anim_utils.ikFkMatch_with_namespace(
        _namespace(),
        "{limb}_blend",
        "{limb}UI_{s}_ctl",
        ["{limb}_{s}_fk0_ctl", "{limb}_{s}_fk1_ctl", "{limb}_{s}_fk2_ctl"],
        "{limb}_{s}_ik_ctl",
        "{limb}_{s}_upv_ctl"{ik_rot})
'''.format(limb=limb, s=side, ik_rot=ik_rot)


def script_space_switch(ui_host, attr, ctl_name):
    """mGear 스페이스 스위치 (클릭하면 스페이스 목록 팝업)."""
    return _NAMESPACE_FUNC + '''
from mgear.anim_picker.handlers import action_handlers
action_handlers.show_space_chage_list(__NAMESPACE__ if __INIT__ else _namespace(),
                                      "{ui}",
                                      "{attr}",
                                      "{ctl}",
                                      __SELF__,
                                      __INIT__)
'''.format(ui=ui_host, attr=attr, ctl=ctl_name)


# --------------------------------------------------------------------------
# BODY 탭
# --------------------------------------------------------------------------
def build_arm(s, sign):
    """sign = +1 (L, 화면 오른쪽) / -1 (R, 화면 왼쪽)."""
    fk = COLOR[s[0] + "_fk"]
    ik = COLOR[s[0] + "_ik"]

    def p(x, y):
        return (x * sign, y)

    return [
        ctl(p(36, 150), 38, 13, fk, ["shoulder_{}_ctl".format(s)]),
        ctl_circle(p(36, 168), 5, ik, ["shoulder_{}_orbit_ctl".format(s)]),
        # FK
        ctl(p(70, 114), 17, 50, fk, ["arm_{}_fk0_ctl".format(s)], radius=8),
        ctl_circle(p(75, 81), 6, ik, ["arm_{}_mid_ctl".format(s)]),
        ctl(p(80, 48), 17, 50, fk, ["arm_{}_fk1_ctl".format(s)], radius=8),
        ctl(p(88, 10), 24, 22, fk, ["arm_{}_fk2_ctl".format(s)]),
        ctl(p(92, -14), 18, 16, fk, ["meta_{}_ctl".format(s)]),
        # IK
        ctl_diamond(p(132, 81), 10, ik, ["arm_{}_upv_ctl".format(s)]),
        ctl(p(134, 10), 30, 30, ik, ["arm_{}_ik_ctl".format(s)], radius=10),
        ctl_circle(p(134, -16), 7, ik, ["arm_{}_ikRot_ctl".format(s)]),
        ctl_diamond(p(132, 136), 8, COLOR["ui"], ["armUI_{}_ctl".format(s)]),
    ]


def build_leg(s, sign):
    fk = COLOR[s[0] + "_fk"]
    ik = COLOR[s[0] + "_ik"]

    def p(x, y):
        return (x * sign, y)

    return [
        ctl_circle(p(30, -30), 6, ik, ["leg_{}_root_ctl".format(s)]),
        # FK
        ctl(p(34, -76), 19, 66, fk, ["leg_{}_fk0_ctl".format(s)], radius=9),
        ctl_circle(p(36, -116), 6, ik, ["leg_{}_mid_ctl".format(s)]),
        ctl(p(38, -158), 19, 66, fk, ["leg_{}_fk1_ctl".format(s)], radius=9),
        ctl(p(40, -204), 24, 18, fk, ["leg_{}_fk2_ctl".format(s)]),
        ctl(p(40, -224), 22, 11, fk, ["foot_{}_fk0_ctl".format(s)], radius=4),
        ctl(p(58, -224), 12, 11, fk, ["foot_{}_fk1_ctl".format(s)], radius=4),
        ctl(p(72, -224), 11, 11, fk, ["foot_{}_fk2_ctl".format(s)], radius=4),
        # IK
        ctl_diamond(p(110, -116), 10, ik, ["leg_{}_upv_ctl".format(s)]),
        ctl(p(114, -204), 42, 20, ik, ["leg_{}_ik_ctl".format(s)], radius=8),
        ctl_circle(p(104, -228), 7, ik, ["foot_{}_roll_ctl".format(s)]),
        ctl_circle(p(126, -228), 5, ik, ["foot_{}_tip_ctl".format(s)]),
        ctl_diamond(p(110, -48), 8, COLOR["ui"], ["legUI_{}_ctl".format(s)]),
    ]


def build_side_panel(s, sign):
    """좌/우 사이드 패널: 그룹 선택 / IK·FK 매칭 / 스페이스 스위치."""
    fk = COLOR[s[0] + "_fk"]
    ik = COLOR[s[0] + "_ik"]
    side_name = "LEFT  (L)" if s[0] == "L" else "RIGHT  (R)"
    x = 262 * sign
    items = [panel(side_name, (x, -6), 104, 624,
                   COLOR["panel_" + s[0]])]

    def group(text, y, color, controls):
        items.append(ctl((x, y), 84, 18, color, controls, text, 8, radius=9))

    def section(text, y):
        items.append(label(text, (x - 42, y), 7, MUTED))

    arm_fk = ["arm_{}_fk{}_ctl".format(s, i) for i in range(3)]
    arm_ik = ["arm_{}_ik_ctl".format(s), "arm_{}_upv_ctl".format(s),
              "arm_{}_ikRot_ctl".format(s)]
    leg_fk = ["leg_{}_fk{}_ctl".format(s, i) for i in range(3)]
    leg_ik = ["leg_{}_ik_ctl".format(s), "leg_{}_upv_ctl".format(s),
              "foot_{}_roll_ctl".format(s)]

    # ---- ARM
    section("ARM", 266)
    group("Arm FK", 248, fk, arm_fk)
    group("Arm IK", 226, ik, arm_ik)
    items.append(button("IK / FK  Match", (x, 202), script_ikfk("arm", s),
                        w=84, h=20, color=COLOR["primary"], text_color=DARK))
    section("ARM SPACE", 174)
    for i, (text, attr, c) in enumerate([
            ("IK", "arm_ikref", "arm_{}_ik_ctl"),
            ("IK Rot", "arm_ikRotRef", "arm_{}_ikRot_ctl"),
            ("UpV", "arm_upvref", "arm_{}_upv_ctl"),
            ("Shoulder", "shoulder_rotRef", "shoulder_{}_orbit_ctl")]):
        items.append(button(
            text, (x, 156 - i * 20),
            script_space_switch("armUI_{}_ctl".format(s), attr, c.format(s)),
            w=84, h=16, size=7))

    # ---- LEG
    section("LEG", 10)
    group("Leg FK", -8, fk, leg_fk)
    group("Leg IK", -30, ik, leg_ik)
    items.append(button("IK / FK  Match", (x, -54), script_ikfk("leg", s),
                        w=84, h=20, color=COLOR["primary"], text_color=DARK))
    section("LEG SPACE", -82)
    for i, (text, attr, c) in enumerate([
            ("IK", "leg_ikref", "leg_{}_ik_ctl"),
            ("UpV", "leg_upvref", "leg_{}_upv_ctl")]):
        items.append(button(
            text, (x, -100 - i * 20),
            script_space_switch("legUI_{}_ctl".format(s), attr, c.format(s)),
            w=84, h=16, size=7))

    # ---- FINGERS (손가락 전체 선택)
    section("HAND", -232)
    fingers = ["thumb_{}_fk{}_ctl".format(s, j) for j in range(3)]
    fingers += ["finger_{}{}_fk{}_ctl".format(s[0], i, j)
                for i in range(4) for j in range(3)]
    group("All Fingers", -250, fk, fingers)
    return items


def build_body_tab():
    c_fk, c_ik = COLOR["C_fk"], COLOR["C_ik"]
    items = []

    # ---- 패널 (가장 먼저 = 가장 뒤에 그려짐)
    items += [
        panel("BODY", (0, -6), 400, 624, COLOR["panel"]),
        panel("TOOLS", (0, -377), 628, 100, COLOR["panel"]),
    ]
    items += build_side_panel("R0", -1) + build_side_panel("L0", 1)

    # ---- root (몸 패널 하단)
    items += [
        ctl((0, -250), 150, 11, COLOR["root"], ["local_C0_ctl"], "local", 6),
        ctl((0, -265), 175, 11, COLOR["root"], ["global_C0_ctl"], "global", 6),
        ctl((0, -280), 200, 11, COLOR["root"], ["world_ctl"], "world", 6),
    ]

    # ---- torso
    items += [
        ctl((0, 6), 124, 14, c_ik, ["body_C0_ctl"], "body", 7, radius=7),
        ctl((0, -12), 74, 13, c_fk, ["hip_C0_ctl"], "hip", 6, radius=6),
        ctl((0, 28), 64, 10, c_ik, ["spine_C0_ik0_ctl"], radius=5),
        ctl((0, 48), 44, 13, c_fk, ["spine_C0_fk0_ctl"]),
        ctl((0, 68), 44, 13, c_fk, ["spine_C0_fk1_ctl"]),
        ctl((0, 88), 44, 13, c_fk, ["spine_C0_fk2_ctl"]),
        ctl((0, 114), 74, 12, c_ik, ["spine_C0_ik1_ctl"], radius=6),
        ctl_diamond((-34, 52), 6, c_ik, ["spine_C0_tan0_ctl"]),
        ctl_diamond((-34, 70), 6, c_ik, ["spine_C0_tan_ctl"]),
        ctl_diamond((-34, 88), 6, c_ik, ["spine_C0_tan1_ctl"]),
        ctl_circle((34, 70), 6, c_ik, ["spine_C0_spinePosition_ctl"]),
        ctl_diamond((0, 134), 7, COLOR["ui"], ["spineUI_C0_ctl"]),
    ]

    # ---- neck / head / eyes
    items += [
        ctl((0, 152), 20, 9, c_fk, ["neck_C0_fk0_ctl"], radius=4),
        ctl((0, 163), 20, 9, c_fk, ["neck_C0_fk1_ctl"], radius=4),
        ctl((0, 174), 20, 9, c_fk, ["neck_C0_fk2_ctl"], radius=4),
        ctl((0, 189), 46, 11, c_ik, ["neck_C0_ik_ctl"], radius=5),
        ctl((0, 222), 50, 46, c_fk, ["neck_C0_head_ctl"], radius=20),
        ctl((0, 258), 54, 10, c_ik, ["eyeslook_C0_ctl"], radius=5),
        ctl_circle((-20, 272), 6, COLOR["R_ik"], ["eye_R0_ik_ctl"]),
        ctl_circle((20, 272), 6, COLOR["L_ik"], ["eye_L0_ik_ctl"]),
        ctl_diamond((44, 238), 8, COLOR["ui"], ["faceUI_C0_ctl"]),
    ]

    # ---- limbs
    items += build_arm("R0", -1) + build_arm("L0", 1)
    items += build_leg("R0", -1) + build_leg("L0", 1)

    # ---- 몸 패널 좌측 상단: 스파인/목 그룹 + 목 스페이스
    spine_fk = ["spine_C0_fk{}_ctl".format(i) for i in range(3)]
    spine_ik = ["spine_C0_ik0_ctl", "spine_C0_ik1_ctl", "spine_C0_tan0_ctl",
                "spine_C0_tan_ctl", "spine_C0_tan1_ctl",
                "spine_C0_spinePosition_ctl"]
    neck_fk = ["neck_C0_fk{}_ctl".format(i) for i in range(3)]
    items += [
        ctl((-150, 268), 72, 16, c_fk, spine_fk, "Spine FK", 7, radius=8),
        ctl((-150, 248), 72, 16, c_ik, spine_ik, "Spine IK", 7, radius=8),
        ctl((150, 268), 72, 16, c_fk, neck_fk, "Neck FK", 7, radius=8),
        button("Head Space", (150, 248),
               script_space_switch("spineUI_C0_ctl", "neck_ikref",
                                   "neck_C0_ik_ctl"),
               w=72, h=16, size=7),
    ]

    # ---- 범례
    legend = [("FK", COLOR["C_fk"]), ("IK", COLOR["C_ik"]),
              ("Settings", COLOR["ui"]), ("Root", COLOR["root"])]
    for i, (text, color) in enumerate(legend):
        x = -180 + i * 52
        items.append(item((x, -300), circle_handles(4), color))
        items.append(label(text, (x + 8, -300), 6, MUTED))

    # ---- TOOLS
    tools = [
        ("Select All", SCRIPT_SELECT_ALL, COLOR["ui"], DARK),
        ("Key All", SCRIPT_KEY_ALL, COLOR["primary"], DARK),
        ("Key Selected", SCRIPT_KEY_SEL, COLOR["button"], WHITE),
        ("Reset Selected", SCRIPT_RESET_SEL, COLOR["button"], WHITE),
        ("Reset All", SCRIPT_RESET_ALL, COLOR["danger"], WHITE),
    ]
    for i, (text, script, color, tcolor) in enumerate(tools):
        items.append(button(text, (-240 + i * 120, -368), script, w=108,
                            h=26, color=color, text_color=tcolor, size=8))
    mirror_tools = [
        ("Copy L \u2192 R", script_copy_side("L", LIMB_PARTS)),
        ("Copy R \u2192 L", script_copy_side("R", LIMB_PARTS)),
        ("Mirror Selected", SCRIPT_MIRROR_SEL),
        ("Flip Selected", SCRIPT_FLIP_SEL),
    ]
    for i, (text, script) in enumerate(mirror_tools):
        items.append(button(text, (-180 + i * 120, -402), script, w=108,
                            h=26, size=8))
    return items


# --------------------------------------------------------------------------
# HANDS 탭
# --------------------------------------------------------------------------
FINGER_NAMES = ["Index", "Middle", "Ring", "Pinky"]


def build_hand(s, sign, cx):
    fk = COLOR[s[0] + "_fk"]
    ik = COLOR[s[0] + "_ik"]
    side_name = "LEFT HAND  (L)" if s[0] == "L" else "RIGHT HAND  (R)"
    items = [panel(side_name, (cx, 14), 280, 320,
                   COLOR["panel_" + s[0]])]

    def p(x, y):
        return (cx + x * sign, y)

    # 손바닥
    items.append(ctl(p(18, -60), 116, 64, fk, ["meta_{}_ctl".format(s)],
                     "meta", 8, radius=16))

    all_fingers = []
    # 손가락: finger_X0~X3 (검지~새끼), fk0(뿌리)~fk2(끝)
    heights = [(46, 40, 34), (50, 44, 36), (46, 40, 34), (38, 32, 28)]
    for i in range(4):
        fx = -18 + i * 30
        name = "finger_{}{}".format(s[0], i)
        chain = ["{}_fk{}_ctl".format(name, j) for j in range(3)]
        all_fingers += chain
        y = -18
        for j, c in enumerate(chain):
            h = heights[i][j]
            items.append(ctl(p(fx, y + h * 0.5 + 4), 22, h, fk, [c],
                             radius=9))
            y += h + 4
        # 손가락 체인 전체 선택
        items.append(ctl(p(fx, y + 16), 26, 14, ik, chain,
                         FINGER_NAMES[i][0], 7, radius=7))

    # 엄지
    t = "thumb_{}".format(s)
    thumb_chain = ["{}_fk{}_ctl".format(t, j) for j in range(3)]
    items.append(ctl_circle(p(-52, -70), 8, ik, ["thumbRoll_{}_ctl".format(s)]))
    for j, c in enumerate(thumb_chain):
        items.append(ctl(p(-64 - j * 18, -36 + j * 34), 20, 30, fk, [c],
                         radius=8))
    items.append(ctl(p(-100, 82), 26, 14, ik, thumb_chain, "T", 7, radius=7))
    all_fingers = thumb_chain + ["thumbRoll_{}_ctl".format(s)] + all_fingers

    # 하단 버튼
    items.append(ctl(p(-48, -122), 100, 20, ik, all_fingers, "All Fingers",
                     8, radius=10))
    items.append(button("Key Fingers", p(64, -122), SCRIPT_KEY_ITEM_CONTROLS,
                        w=100, h=20, color=COLOR["primary"], text_color=DARK,
                        controls=all_fingers))
    return items


def build_hands_tab():
    items = []
    items += build_hand("R0", -1, -150)
    items += build_hand("L0", 1, 150)
    items += [
        panel("TOOLS", (0, -206), 580, 50, COLOR["panel"]),
        button("Hand L \u2192 R", (-180, -214),
               script_copy_side("L", HAND_PARTS), w=108, h=24),
        button("Hand R \u2192 L", (-60, -214),
               script_copy_side("R", HAND_PARTS), w=108, h=24),
        button("Key Selected", (60, -214), SCRIPT_KEY_SEL, w=108, h=24),
        button("Reset Selected", (180, -214), SCRIPT_RESET_SEL, w=108, h=24),
    ]
    return items


# --------------------------------------------------------------------------
# SVG 미리보기 (Maya 없이 레이아웃 확인용 - Anim Picker 화면을 흉내냄)
# --------------------------------------------------------------------------
def write_svg_preview(items, path, pad=24):
    xs, ys = [], []
    for it in items:
        px, py = it["position"]
        for hx, hy in it["handles"]:
            xs.append(px + hx)
            ys.append(py + hy)
    minx, maxx = min(xs) - pad, max(xs) + pad
    miny, maxy = min(ys) - pad, max(ys) + pad
    w, h = maxx - minx, maxy - miny

    def tx(x, y):  # Y-up -> SVG Y-down
        return x - minx, maxy - y

    def rgb(c):
        return "rgb({},{},{})".format(c[0], c[1], c[2])

    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="{:.0f}" '
           'height="{:.0f}" viewBox="0 0 {:.0f} {:.0f}" '
           'font-family="Segoe UI, Helvetica, Arial, sans-serif">'.format(
               w * 1.6, h * 1.6, w, h),
           '<rect width="100%" height="100%" fill="#444444"/>']
    for it in items:
        px, py = it["position"]
        color = it["color"]
        alpha = color[3] / 255.0
        if it.get("backdrop"):
            hx = [p[0] for p in it["handles"]]
            hy = [p[1] for p in it["handles"]]
            x0, y0 = tx(px + min(hx), py + max(hy))
            bw, bh = max(hx) - min(hx), max(hy) - min(hy)
            rad = it.get("corner_radius", 8)
            clip = "clip{}".format(id(it))
            out.append('<clipPath id="{}"><rect x="{:.1f}" y="{:.1f}" '
                       'width="{:.1f}" height="{:.1f}" rx="{}"/></clipPath>'
                       .format(clip, x0, y0, bw, bh, rad))
            out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" '
                       'height="{:.1f}" rx="{}" fill="{}" fill-opacity="{:.2f}" '
                       'stroke="{}" stroke-opacity="{:.2f}" stroke-width="1"/>'
                       .format(x0, y0, bw, bh, rad, rgb(color), alpha,
                               rgb(color), min(1.0, alpha + 90 / 255.0)))
            out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" '
                       'height="18" fill="{}" fill-opacity="{:.2f}" '
                       'clip-path="url(#{})"/>'.format(
                           x0, y0, bw, rgb(color),
                           min(1.0, alpha + 60 / 255.0), clip))
            out.append('<text x="{:.1f}" y="{:.1f}" font-size="10.8" '
                       'dominant-baseline="middle" fill="#ebebeb">{}</text>'
                       .format(x0 + 6, y0 + 9, it.get("title", "")))
            continue
        if alpha > 0:
            pts = " ".join("{:.2f},{:.2f}".format(*tx(px + hx, py + hy))
                           for hx, hy in it["handles"])
            out.append('<polygon points="{}" fill="{}" fill-opacity="{:.2f}"/>'
                       .format(pts, rgb(color), alpha))
        if "text" in it:
            x, y = tx(px, py)
            anchor = "middle" if alpha > 0 else "start"
            out.append('<text x="{:.2f}" y="{:.2f}" font-size="{}" '
                       'text-anchor="{}" dominant-baseline="middle" '
                       'font-weight="600" fill="{}">{}</text>'.format(
                           x, y, it["text_size"], anchor,
                           rgb(it["text_color"]), it["text"]))
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out))


# --------------------------------------------------------------------------
def build():
    tabs = [
        ("Body", build_body_tab()),
        ("Hands", build_hands_tab()),
    ]
    data = {"tabs": [{"name": name, "data": {"items": items}}
                     for name, items in tabs]}

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    pkr = os.path.join(OUT_DIR, OUT_NAME + ".pkr")
    with open(pkr, "w") as f:
        json.dump(data, f, sort_keys=False, indent=4)
    print("wrote", pkr)

    for name, items in tabs:
        svg = os.path.join(OUT_DIR, "{}_{}.svg".format(OUT_NAME, name.lower()))
        write_svg_preview(items, svg)
        print("wrote", svg)

    ctls = sorted({c for _, items in tabs for it in items
                   for c in it.get("controls", [])})
    print("{} tabs, {} items, {} unique controls".format(
        len(tabs), sum(len(i) for _, i in tabs), len(ctls)))
    return data


if __name__ == "__main__":
    build()

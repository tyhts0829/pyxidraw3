import os
import pickle
import sys
from pathlib import Path
from typing import Optional

import mido
from icecream import ic

from .helpers import DualKeyDict

# from midi.ui.controllers.tx6 import TX6Dict


class MidiController:
    MSB_THRESHOLD = 32  # 14ビットのコントロールチェンジメッセージのMSBの値は32以下
    SCALED_14BIT_MIN = 0  # 14ビットのMIDI値をスケール変換したときの最小値
    SCALED_14BIT_MAX = 127  # 14ビットのMIDI値をスケール変換したときの最大値
    MAX_14BIT_VAL = 16383  # 14ビットのMIDI値の最大値
    SAVE_DIR = Path(__file__).parent / "cc"

    def __init__(self, port_name, cc_map, mode):
        self.port_name = port_name
        self.cc_map = cc_map
        self.inport = self.validate_and_open_port(port_name)
        self.mode = mode
        self.msb_values = {}
        self.cc = self.init_cc()

        self.sync_grid_knob_values()
        self.enable_debug = False

    def __repr__(self):
        return f"MidiController(port_name={self.port_name}, mode={self.mode})"

    def init_cc(self):
        try:
            cc = self.load_cc()
            cc.reset_activation()
        except:
            cc = DualKeyDict()
            cc.init_map(self.cc_map)
        return cc

    def load_cc(self):
        """pklからself.ccを読み込む。"""
        script_name = os.path.basename(sys.argv[0])[:-3]  # .pyを除いたスクリプト名
        file_name = f"{script_name}_{self.port_name}.pkl"
        MidiController.SAVE_DIR.mkdir(exist_ok=True)
        with open(MidiController.SAVE_DIR / file_name, "rb") as f:
            cc = pickle.load(f)
        return cc

    def save_cc(self):
        """self.ccをpklに保存する。"""
        script_name = os.path.basename(sys.argv[0])[:-3]  # .pyを除いたスクリプト名
        save_name = f"{script_name}_{self.port_name}.pkl"
        MidiController.SAVE_DIR.mkdir(exist_ok=True)
        with open(MidiController.SAVE_DIR / save_name, "wb") as f:
            pickle.dump(self.cc, f)

    def update_cc(self, msg):
        """
        MIDIメッセージを受け取り、self.ccの値を更新する。
        port_nameに応じてccの範囲を変更する。
        """
        result = self.process_midi_message(msg)
        if result and "type" in result and result["type"] in ["CC(14bit)", "CC(7bit)"]:
            result["value"] /= 127
            cc_number = result["CC number"]
            self.cc[cc_number] = result["value"]
            if self.enable_debug:
                ic(self.cc)

    @staticmethod
    def validate_and_open_port(port_name):
        if port_name in mido.get_input_names():  # type: ignore
            return mido.open_input(port_name)  # type: ignore
        else:
            MidiController.handle_invalid_port_name(port_name)

    @staticmethod
    def handle_invalid_port_name(port_name: str) -> None:
        print(f"Invalid port name: {port_name}")
        print("Available ports are:", mido.get_input_names())  # type: ignore
        exit(1)

    def process_midi_message(self, msg: mido.Message) -> Optional[dict]:
        if msg.type == "control_change":  # type: ignore
            return self.handle_control_change(msg)
        elif msg.type in ["note_on", "note_off"]:  # type: ignore
            return {"type": "Note", "note": msg.note, "velocity": msg.velocity}  # type: ignore
        else:
            return None

    def handle_control_change(self, msg):
        if self.mode == "14bit":
            return self.process_14bit_control_change(msg)
        elif self.mode == "7bit":
            return self.process_7bit_control_change(msg)

    def process_14bit_control_change(self, msg: mido.Message) -> Optional[dict]:
        control_change_number = msg.control  # type: ignore

        if control_change_number < self.MSB_THRESHOLD:  # MSB
            # MSBを保存
            self.msb_values[control_change_number] = msg.value  # type: ignore
            return None  # LSBがまだ届いていないため、何もしない
        else:  # LSB
            return self.calc_combined_value(control_change_number, msg.value)  # type: ignore

    def process_7bit_control_change(self, msg: mido.Message) -> dict:
        return {"type": "CC(7bit)", "CC number": msg.control, "value": msg.value}  # type: ignore

    def calc_combined_value(self, control_change_number: int, value: int) -> Optional[dict]:
        msb_control = control_change_number - MidiController.MSB_THRESHOLD
        if msb_control in self.msb_values:
            # MSBとLSBから14ビット値を計算
            msb = self.msb_values[msb_control]
            lsb = value
            value_14bit = (msb << 7) | lsb
            scaled_value_14bit = MidiController.scale_value(
                value_14bit, MidiController.SCALED_14BIT_MIN, MidiController.SCALED_14BIT_MAX
            )
            return {"type": "CC(14bit)", "CC number": msb_control, "value": scaled_value_14bit}

    @staticmethod
    def scale_value(value_14bit: int, min_val: float, max_val: float) -> float:
        normalized = value_14bit / MidiController.MAX_14BIT_VAL
        return min_val + (max_val - min_val) * normalized  # 正規化された値を新しい範囲にスケール変換

    def set_debug(self, debug: bool):
        self.enable_debug = debug

    def sync_grid_knob_values(self):
        try:
            grid_output_port_name = [name for name in mido.get_output_names() if "Intech Grid MIDI device" in name][0]  # type: ignore
        except:
            return
        with mido.open_output(grid_output_port_name) as outport:  # type: ignore
            msg = mido.Message("control_change", channel=0, control=64, value=127)
            outport.send(msg)

    @staticmethod
    def show_available_ports() -> None:
        print("Available ports:")
        print("  input: ", mido.get_input_names())  # type: ignore
        print("  output: ", mido.get_output_names())  # type: ignore

    def iter_pending(self) -> mido.Message:
        """MIDIメッセージをイテレータとして返す。"""
        return self.inport.iter_pending()  # type: ignore


if __name__ == "__main__":
    import arc

    arc.run()
    MidiController.show_available_ports()

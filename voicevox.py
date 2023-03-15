from pathlib import Path
from voicevox_core import VoicevoxCore, METAS
from pprint import pprint

core = VoicevoxCore(open_jtalk_dict_dir=Path("../open_jtalk_dic_utf_8-1.11"))
# pprint(METAS)


def create_voice(msg,speaker_id):
    if not core.is_model_loaded(speaker_id):
        core.load_model(speaker_id)
    wave_bytes = core.tts(msg,speaker_id)
    with open("./temp/output.wav","wb") as f:
      f.write(wave_bytes)

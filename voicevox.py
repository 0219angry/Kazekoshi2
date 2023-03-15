from pathlib import Path
from voicevox_core import VoicevoxCore, METAS
from pprint import pprint

core = VoicevoxCore(open_jtalk_dict_dir=Path("../open_jtalk_dic_utf_8-1.11"))


pprint(METAS)
# for i in range(1,len(METAS)):
#     filtered = list(filter(lambda x: x.name=="ノーマル",METAS[i].styles))
#     if len(filtered) == 1:
#         print(METAS[i].name,filtered[0].id)
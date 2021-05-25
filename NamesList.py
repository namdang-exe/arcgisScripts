import os

names = ["LRS_RINV_Divided", "LRSE_EvacuationRoute"]
for name in names:
    os.system("python FeatureUpdate.py {}".format(name))

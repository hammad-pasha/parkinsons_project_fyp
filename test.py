#Speech Assessment module

import joblib
import pandas as pd
import numpy as np, os

import parselmouth as pm

main_df = pd.DataFrame(columns=["patient_type","Jitter_rel", "Jitter_abs", "Jitter_RAP", "Jitter_PPQ", "Shim_loc", "Shim_dB",
                                "Shim_APQ3", "Shim_APQ5", "Shi_APQ11", "hnr05", "hnr15",
                                "hnr25"])

def extractFeatures(voiceID, f0min, f0max, unit):
    sound = pm.Sound(voiceID) # read the sound
    pitch = pm.praat.call(sound, "To Pitch", 0.0, f0min, f0max)
    pointProcess = pm.praat.call(sound, "To PointProcess (periodic, cc)", f0min, f0max)#create a praat pitch object
    localJitter = pm.praat.call(pointProcess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    localabsoluteJitter = pm.praat.call(pointProcess, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3)
    rapJitter = pm.praat.call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
    ppq5Jitter = pm.praat.call(pointProcess, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
    localShimmer =  pm.praat.call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    localdbShimmer = pm.praat.call([sound, pointProcess], "Get shimmer (local_dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    apq3Shimmer = pm.praat.call([sound, pointProcess], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    aqpq5Shimmer = pm.praat.call([sound, pointProcess], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    apq11Shimmer =  pm.praat.call([sound, pointProcess], "Get shimmer (apq11)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    harmonicity05 = pm.praat.call(sound, "To Harmonicity (cc)", 0.01, 500, 0.1, 1.0)
    hnr05 = pm.praat.call(harmonicity05, "Get mean", 0, 0)
    harmonicity15 = pm.praat.call(sound, "To Harmonicity (cc)", 0.01, 1500, 0.1, 1.0)
    hnr15 = pm.praat.call(harmonicity15, "Get mean", 0, 0)
    harmonicity25 = pm.praat.call(sound, "To Harmonicity (cc)", 0.01, 2500, 0.1, 1.0)
    hnr25 = pm.praat.call(harmonicity25, "Get mean", 0, 0)
    harmonicity35 = pm.praat.call(sound, "To Harmonicity (cc)", 0.01, 3500, 0.1, 1.0)
    hnr35 = pm.praat.call(harmonicity35, "Get mean", 0, 0)
    harmonicity38 = pm.praat.call(sound, "To Harmonicity (cc)", 0.01, 3800, 0.1, 1.0)
    hnr38 = pm.praat.call(harmonicity38, "Get mean", 0, 0)
    return localJitter, localabsoluteJitter, rapJitter, ppq5Jitter, localShimmer, localdbShimmer, apq3Shimmer, aqpq5Shimmer, apq11Shimmer, hnr05, hnr15 ,hnr25 ,hnr35 ,hnr38


def predict(audioPath,modelPath,patient_type):
    global main_df
    localJitter_list = []
    localabsoluteJitter_list = []
    rapJitter_list = []
    ppq5Jitter_list = []
    localShimmer_list = []
    localdbShimmer_list = []
    apq3Shimmer_list = []
    aqpq5Shimmer_list = []
    apq11Shimmer_list = []
    hnr05_list = []
    hnr15_list = []
    hnr25_list = []
    hnr35_list = []
    hnr38_list = []

    sound = pm.Sound(audioPath)
    (localJitter, localabsoluteJitter, rapJitter, ppq5Jitter, localShimmer, localdbShimmer, apq3Shimmer, aqpq5Shimmer,
     apq11Shimmer, hnr05, hnr15, hnr25, hnr35, hnr38) = extractFeatures(sound, 75, 1000, "Hertz")
    localJitter_list.append(localJitter) 
    localabsoluteJitter_list.append(localabsoluteJitter) 
    rapJitter_list.append(rapJitter)
    ppq5Jitter_list.append(ppq5Jitter)
    localShimmer_list.append(localShimmer)
    localdbShimmer_list.append(localdbShimmer)
    apq3Shimmer_list.append(apq3Shimmer)
    aqpq5Shimmer_list.append(aqpq5Shimmer)
    apq11Shimmer_list.append(apq11Shimmer)
    hnr05_list.append(hnr05)
    hnr15_list.append(hnr15)
    hnr25_list.append(hnr25)
    hnr35_list.append(hnr35)
    hnr38_list.append(hnr38)

    predictiontDF = pd.DataFrame(np.column_stack(
        [patient_type, localJitter_list, localabsoluteJitter_list, rapJitter_list, ppq5Jitter_list, localShimmer_list,
        localdbShimmer_list, apq3Shimmer_list, aqpq5Shimmer_list, apq11Shimmer_list, hnr05_list, hnr15_list, hnr25_list]),
        columns=["patient_type","Jitter_rel", "Jitter_abs", "Jitter_RAP", "Jitter_PPQ", "Shim_loc", "Shim_dB",
        "Shim_APQ3", "Shim_APQ5", "Shi_APQ11", "hnr05", "hnr15",
        "hnr25"])

    main_df = pd.DataFrame(np.concatenate([main_df.values, predictiontDF.values]), columns=main_df.columns)

    #KNN -> 91.6 Accuracy
    #SVM & Linear Regression -> 72%
    # model = joblib.load(modelPath)
    # print("Predicting...")
    # result = model.predict(predictiontDF)
    # result = str(result)

    # if result == "[1]":
    #     return "Parkinson detected"
    # else:
    #     return "Parkinson not detected"

# result = predict("audio/Healthy/m1.wav" , "models/KNNModel.sav")
# print("Result: " + result)

hp_audios = os.listdir("audio/Healthy")
uhp_audios = os.listdir("audio/Unhealthy")

for audio in hp_audios:
    print("Processing: " + "HP "+audio + "...")
    predict("audio/Healthy/"+audio,"","1")

for audio in uhp_audios:
    print("Processing: " + "UHP "+audio + "...")
    predict("audio/Unhealthy/"+audio,"","0")

main_df.to_csv("audio_dataset.csv",index=False)

print(len(main_df))



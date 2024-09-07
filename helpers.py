import cv2
import mediapipe as mp
import numpy as np, os
import math
import joblib, os
import pandas as pd
import parselmouth as pm

classList=[]

def calc_distance(p11, p22):
    p1 = np.array(p11)
    p2 = np.array(p22)

    return round(math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2),2) # Pythagorean theorem

#Helper functions
def quickPrint(li):
    for d in li:
        print(d)

def getX(list):
    x = []
    for d in list:
        x.append(d[0])
    return x
def getY(list):
    x = []
    for d in list:
        x.append(d[1])
    return x

def getClassList(li,patientType):
    for d in li:
        classList.append(int(patientType))

#Calculate AVG
def calculateAvg(list1):
    sum = 0
    # if len(list1) == 0:
     #     return 0
    for d in list1:
        sum += d
    return sum/len(list1)



def predict(videoPath,showVideo):
  


    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(videoPath)

    right_shoulder = []
    right_elbow = []
    right_wrist = []
    right_hip = []
    right_knee = []
    right_ankle = []
    right_heel = []
    right_foot_index = []

    left_shoulder = []
    left_elbow = []
    left_wrist = []
    left_hip = []
    left_knee = []
    left_ankle = []
    left_heel = []
    left_foot_index = []

    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():    
            ret,frame = cap.read()
            if ret is False:
                break

            image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            #Detections
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            
            #Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                print("Extracting Features...")


                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                l_heel = [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]
                l_foot_index = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]

                shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                heel = [landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y]
                foot_index = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]

                right_shoulder.append(shoulder)
                right_elbow.append(elbow)
                right_wrist.append(wrist)
                right_hip.append(hip)
                right_knee.append(knee)
                right_ankle.append(ankle)
                right_heel.append(heel)
                right_foot_index.append(foot_index)

                left_shoulder.append(l_shoulder)
                left_elbow.append(l_elbow)
                left_wrist.append(l_wrist)
                left_hip.append(l_hip)
                left_knee.append(l_knee)
                left_ankle.append(l_ankle)
                left_heel.append(l_heel)
                left_foot_index.append(l_foot_index)


                # cv2.putText(image,"Hand Swinged:"+str(0), fontLocation, font, fontScale,fontColor,thickness,lineType)
            
            except:
                pass

            #Apply Joints Rendering
            mp_drawing.draw_landmarks(image,results.pose_landmarks,mp_pose.POSE_CONNECTIONS ,
                                    mp_drawing.DrawingSpec(color=(255,100,22),thickness=3,circle_radius=3),
                                    mp_drawing.DrawingSpec(color=(255,189 ,22),thickness=3,circle_radius=3),)

            if showVideo:
                cv2.imshow("Gait Extractor" , image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    # print(right_shoulder, right_elbow, right_wrist, right_hip, right_knee, right_ankle, right_heel, right_foot_index, sep="\n")
    #Extract x and y from the respective joints
    right_shoulder_x = getX(right_shoulder)
    right_shoulder_y = getY(right_shoulder)
    left_shoulder_x = getX(left_shoulder)
    left_shoulder_y = getY(left_shoulder)

    right_elbow_x = getX(right_elbow)
    right_elbow_y = getY(right_elbow)
    left_elbow_x = getX(left_elbow)
    left_elbow_y = getY(left_elbow)

    right_wrist_x = getX(right_wrist)
    right_wrist_y = getY(right_wrist)
    left_wrist_x = getX(left_wrist)
    left_wrist_y = getY(left_wrist)

    right_hip_x = getX(right_hip)
    right_hip_y = getY(right_hip)
    left_hip_x = getX(left_hip)
    left_hip_y = getY(left_hip)

    right_knee_x = getX(right_knee)
    right_knee_y = getY(right_knee)
    left_knee_x = getX(left_knee)
    left_knee_y = getY(left_knee)

    right_ankle_x = getX(right_ankle)
    right_ankle_y = getY(right_ankle)
    left_ankle_x = getX(left_ankle)
    left_ankle_y = getY(left_ankle)

    right_heel_x = getX(right_heel)
    right_heel_y = getY(right_heel)
    left_heel_x = getX(left_heel)
    left_heel_y = getY(left_heel)

    right_foot_index_x = getX(right_foot_index)
    right_foot_index_y = getY(right_foot_index)
    left_foot_index_x = getX(left_foot_index)
    left_foot_index_y = getY(left_foot_index)

    # getClassList(right_shoulder,paitentType)

    #CALCULATING AVG
    shoulder_x_avg = calculateAvg(right_shoulder_x)
    shoulder_y_avg = calculateAvg(right_shoulder_y)
    left_shoulder_x_avg = calculateAvg(left_shoulder_x)
    left_shoulder_y_avg = calculateAvg(left_shoulder_y)

    elbow_x_avg = calculateAvg(right_elbow_x)
    elbow_y_avg = calculateAvg(right_elbow_y)
    left_elbow_x_avg = calculateAvg(left_elbow_x)
    left_elbow_y_avg = calculateAvg(left_elbow_y)

    wrist_x_avg = calculateAvg(right_wrist_x)
    wrist_y_avg = calculateAvg(right_wrist_y)
    left_wrist_x_avg = calculateAvg(left_wrist_x)
    left_wrist_y_avg = calculateAvg(left_wrist_y)

    hip_x_avg = calculateAvg(right_hip_x)
    hip_y_avg = calculateAvg(right_hip_y)
    left_hip_x_avg = calculateAvg(left_hip_x)
    left_hip_y_avg = calculateAvg(left_hip_y)

    knee_x_avg = calculateAvg(right_knee_x)
    knee_y_avg = calculateAvg(right_knee_y)
    left_knee_x_avg = calculateAvg(left_knee_x)
    left_knee_y_avg = calculateAvg(left_knee_y)

    ankle_x_avg = calculateAvg(right_ankle_x)
    ankle_y_avg = calculateAvg(right_ankle_y)
    left_ankle_x_avg = calculateAvg(left_ankle_x)
    left_ankle_y_avg = calculateAvg(left_ankle_y)

    heel_x_avg = calculateAvg(right_heel_x)
    heel_y_avg = calculateAvg(right_heel_y)
    left_heel_x_avg = calculateAvg(left_heel_x)
    left_heel_y_avg = calculateAvg(left_heel_y)

    foot_index_x_avg = calculateAvg(right_foot_index_x)
    foot_index_y_avg = calculateAvg(right_foot_index_y)
    left_foot_index_x_avg = calculateAvg(left_foot_index_x)
    left_foot_index_y_avg = calculateAvg(left_foot_index_y)

    #Clear every list
    right_shoulder_x.clear()
    right_shoulder_y.clear()
    left_shoulder_x.clear()
    left_shoulder_y.clear()

    right_elbow_x.clear()
    right_elbow_y.clear()
    left_elbow_x.clear()
    left_elbow_y.clear()

    right_wrist_x.clear()
    right_wrist_y.clear()
    left_wrist_x.clear()
    left_wrist_y.clear()

    right_hip_x.clear()
    right_hip_y.clear()
    left_hip_x.clear()
    left_hip_y.clear()

    right_knee_x.clear()
    right_knee_y.clear()
    left_knee_x.clear()
    left_knee_y.clear()

    right_ankle_x.clear()
    right_ankle_y.clear()
    left_ankle_x.clear()
    left_ankle_y.clear()

    right_heel_x.clear()
    right_heel_y.clear()
    left_heel_x.clear()
    left_heel_y.clear()

    right_foot_index_x.clear()
    right_foot_index_y.clear()
    left_foot_index_x.clear()
    left_foot_index_y.clear()

    #Append Averages to list
    right_shoulder_x.append(shoulder_x_avg)
    right_shoulder_y.append(shoulder_y_avg)
    left_shoulder_x.append(left_shoulder_x_avg)
    left_shoulder_y.append(left_shoulder_y_avg)

    right_elbow_x.append(elbow_x_avg)
    right_elbow_y.append(elbow_y_avg)
    left_elbow_x.append(left_elbow_x_avg)
    left_elbow_y.append(left_elbow_y_avg)

    right_wrist_x.append(wrist_x_avg)
    right_wrist_y.append(wrist_y_avg)
    left_wrist_x.append(left_wrist_x_avg)
    left_wrist_y.append(left_wrist_y_avg)

    right_hip_x.append(hip_x_avg)
    right_hip_y.append(hip_y_avg)
    left_hip_x.append(left_hip_x_avg)
    left_hip_y.append(left_hip_y_avg)

    right_knee_x.append(knee_x_avg)
    right_knee_y.append(knee_y_avg)
    left_knee_x.append(left_knee_x_avg)
    left_knee_y.append(left_knee_y_avg)

    right_ankle_x.append(ankle_x_avg)
    right_ankle_y.append(ankle_y_avg)
    left_ankle_x.append(left_ankle_x_avg)
    left_ankle_y.append(left_ankle_y_avg)

    right_heel_x.append(heel_x_avg)
    right_heel_y.append(heel_y_avg)
    left_heel_x.append(left_heel_x_avg)
    left_heel_y.append(left_heel_y_avg)

    right_foot_index_x.append(foot_index_x_avg)
    right_foot_index_y.append(foot_index_y_avg)
    left_foot_index_x.append(left_foot_index_x_avg)
    left_foot_index_y.append(left_foot_index_y_avg)

    print(right_foot_index_x)

    df = pd.DataFrame([right_shoulder_x,right_shoulder_y,right_elbow_x,right_elbow_y,
                                    right_wrist_x,right_wrist_y,right_hip_x,right_hip_y,right_knee_x,right_knee_y,right_ankle_x,
                                    right_ankle_y,right_heel_x,right_heel_y,right_foot_index_x,right_foot_index_y,
                                    left_shoulder_x,left_shoulder_y,left_elbow_x,left_elbow_y,left_wrist_x,left_wrist_y,
                                    left_hip_x,left_hip_y,left_knee_x,left_knee_y,left_ankle_x,left_ankle_y,left_heel_x,
                                    left_heel_y,left_foot_index_x,left_foot_index_y],
                    index=['right_shoulder_x','right_shoulder_y','right_elbow_x','right_elbow_y','right_wrist_x',
                    'right_wrist_y','right_hip_x','right_hip_y','right_knee_x','right_knee_y','right_ankle_x','right_ankle_y',
                    'right_heel_x','right_heel_y','right_foot_index_x','right_foot_index_y', 'left_shoulder_x',
                    'left_shoulder_y','left_elbow_x','left_elbow_y','left_wrist_x','left_wrist_y','left_hip_x','left_hip_y',
                    'left_knee_x','left_knee_y','left_ankle_x','left_ankle_y','left_heel_x','left_heel_y','left_foot_index_x',
                    'left_foot_index_y']).T
    
    df.to_csv('data.csv',index=False)

    return df

#Speech Assessment module

# main_df = pd.DataFrame(columns=["patient_type","Jitter_rel", "Jitter_abs", "Jitter_RAP", "Jitter_PPQ", "Shim_loc", "Shim_dB",
#                                 "Shim_APQ3", "Shim_APQ5", "Shi_APQ11", "hnr05", "hnr15",
#                                 "hnr25"])

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


def helper_predict_speech(audioPath,patient_type=1): # removed modelPath as a parameter. as it wasnt being used 
    main_df = pd.read_csv("audio_dataset.csv")
    
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
    main_df.to_csv("audio_dataset.csv",index=False)

    return predictiontDF

# result = predict("audio/Healthy/m1.wav" , "models/KNNModel.sav")
# print("Result: " + result)

# hp_audios = os.listdir("audio/Healthy")
# uhp_audios = os.listdir("audio/Unhealthy")

# for audio in hp_audios:
#     print("Processing: " + "HP "+audio + "...")
#     predict("audio/Healthy/"+audio,"","1")

# for audio in uhp_audios:
#     print("Processing: " + "UHP "+audio + "...")
#     predict("audio/Unhealthy/"+audio,"","0")


# print(len(main_df))
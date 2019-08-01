#-*- coding: utf-8 -*-
import json
import cv2
import requests
import time
import random
import pygame
import numpy as np
# FaceAPIを使うためのキー
API_KEY ='052c72c5a68b43c3a1a85d67acf21d5b'
# 自分のMicroOfficeアカウント内のFaceIDへのURL
api_url = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0/detect'
#カメラからの画像を保存するためのfileのfile名
picture_file = 'application1.jpg'
#0番目のカメラに対するキャプチャ構造体を作成する
cap = cv2.VideoCapture(0)
#requestsを使う際のリクエストヘッダ
headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': API_KEY,
    }
#requestsを使う際のURLパラメータ
params = {
    'returnFaceId': 'false',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'emotion',
    }
#扱う感情のリスト
emotion_list = ["anger","contempt","disgust","fear","happiness","sadness","surprise"]
#お題の感情を入れる変数の初期化（最初は幸せ）
emotion_target = "happiness"
#成功した際に表示されるそれぞれの表情のイラストのリスト
emotion_illustration = ['anger.jpg','contempt.jpg','disgust.jpg','fear.jpg','happiness.png','sadness.jpg','surprise.png']
#お題の感情が配列の何番目に当たるかを表す変数の初期化（最初はhappinessなので4）
emotion_number = 4
#結果発表のwindowの背景画像
result_picture = 'white.png'
#pygameのmixerモジュールの初期化
pygame.mixer.init()
#再生する音楽ファイルを読み込む
pygame.mixer.music.load("cheer.mp3")
#スコアを表す変数の初期化
score = 0
#ウィンドウに表示するフレーズの初期化
next_frase = ""
#ゲームの始まりの時刻を取得
t1 = time.time()
#表示用ウィンドウの初期化
cv2.namedWindow("Capture")

for i in range(60000):
    #カメラから画像をキャプチャする（retにはキャプチャできたかどうかのbool値が入る）
    ret, frame = cap.read()
    #100msに一回表情を採点する
    if (i % 100) == 0:
        t2 = time.time()
        #制限時間（ここでは60秒に設定されている）が終わったらループから抜け出す
        if (t2-t1) > 60:
            break
        #カメラからの画像をファイルに書き込む
        cv2.imwrite(picture_file, frame)
        #上のファイルを読み込みバイナリモードで開く
        with open(picture_file,'rb') as f:
            #ファイルから画像を代入
            image = f.read()
            #FaceAPIと通信し解析結果を受け取る
            response = requests.post(api_url,params=params,headers=headers,data=image)
            #解析結果の内容を辞書のリストに変換して取得
            data = response.json()
            for id in range(len(data)):
                rect = data[id]["faceRectangle"]
                #顔として認識されている長方形の左上の点のy座標
                top = int(rect["top"])
                #顔として認識されている長方形の左上の点のx座標
                left = int(rect["left"])
                #顔として認識されている長方形の右下の点のy座標
                btm = top + int(rect["height"])
                #顔として認識されている長方形の右下の点のx座標
                right = left + int(rect["width"])
                #画像の中に顔として認識されている部分の長方形を作成
                cv2.rectangle(frame, (left,top),(right,btm),(255,255,255),3)
                #カメラから受け取った顔のお題となっている感情をどのくらい表しているかをパラメータとして代入
                emotion_parameter = data[id]["faceAttributes"]["emotion"][emotion_target]
                #現在の表情がどの程度で採点されたかを表すフレーズの設定
                now_parameter_frase = ("{0}:{1}".format(emotion_target, emotion_parameter))
                #成功だったときの処理（ここではパラメータが0.6以上で成功としている
                if emotion_parameter > 0.6:
                    #拍手の音声を一回だけ流す
                    pygame.mixer.music.play(1)
                    #成功したので10点加点
                    score = score + 10
                    #次のお題を決めるために0~6でランダムに値を代入
                    random_number = random.randint(0,6)
                    #感情のリストのうち上のランダム値番目の感情が次のお題
                    emotion_target = emotion_list[random_number]
                    #ウィンドウに表示するフレーズを設定
                    next_frase=("Next is {0}".format(emotion_target))
                    #ウィンドウの顔として認識される部分（長方形）の上にGreat!!!と表示
                    cv2.putText(frame,"Great!!!",(left-5,top-10),0,3,(0,0,255),2,cv2.LINE_AA)
                    #先程設定したフレーズをウィンドウ下部に表示
                    cv2.putText(frame,next_frase,(15,450),0,2,(255,0,0),2,cv2.LINE_AA)
                    #成功したお題の感情に該当するイラストを変数に代入
                    img = cv2.imread(emotion_illustration[emotion_number])
                    #イラストのサイズを変更
                    img = cv2.resize(img,(200,200))
                    #カメラからの画像からイラストを表示したい部分のみを引き出して変数に代入
                    roi1 = frame[140:340,10:210]
                    roi2 = frame[140:340,430:630]
                    #引き出した部分とイラストを合成
                    final_roi1 = cv2.bitwise_or(roi1,img)
                    final_roi2 = cv2.bitwise_or(roi2,img)
                    #引き出した箇所を合成したイラストに変更
                    frame[140:340, 10:210] = final_roi1
                    frame[140:340, 430:630] = final_roi2
                    #次のお題の感情を表す数字を変数に代入
                    emotion_number = random_number
                    cv2.imshow("Capture", frame)
                    c = cv2.waitKey(1000)
    #現在自分の表情がどの程度で採点されたか表示                
    cv2.putText(frame,now_parameter_frase,(100,50),0,2,(100,100,0),2,cv2.LINE_AA)   #お題となる感情の表示             
    cv2.putText(frame,next_frase,(15,450),0,2,(255,0,0),2,cv2.LINE_AA)          
    #ウィンドウに画像を表示
    cv2.imshow("Capture", frame)
    #1ms間を空ける
    c = cv2.waitKey(1)
    #Escキーが押されたらゲーム中止
    if c == 27:
        break
#結果発表の画像を読み込む
result_image = cv2.imread(result_picture)
#画像をwindowの大きさに合うようにサイズ変更
result_image = cv2.resize(result_image,(640,480))
#画像の適切な位置にYour scoreを貼り付け
cv2.putText(result_image," Your score",(result_image.shape[1]/5,result_image.shape[0]/4),0,2,(0,0,0),1,cv2.LINE_AA)
#画像の適切な位置に点数を貼り付け
cv2.putText(result_image,"{0}".format(score),(result_image.shape[1]*3/7,result_image.shape[0]*2/3),0,2,(0,0,0),1,cv2.LINE_AA)
#ウィンドウに画像を表示
cv2.imshow("Capture",result_image)
#2000ms待機
b = cv2.waitKey(2000)
#ウィンドウの開放
cap.release()

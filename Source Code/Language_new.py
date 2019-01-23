import numpy as np
import math,random
import speech_recognition as sr
import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
#lang=['dutch','english','french','german','japanese','mandarin','random','spanish']
lang=['english','mandarin','random']
leng=20
#----create Dataset-----#

dataset=[]

dataset_test=[]

dataset_len=0

for i in range(len(lang)):
	file = open("data/"+lang[i]+".txt",'r')
	str1=file.read().split("\n")
	for j in str1:
		data=j.split(',')
		if len(data[0])<leng:
			if dataset_len%4!=0:
				dataset.append([data[0].upper(),i])
				dataset_len+=1

			else:
				dataset_test.append([data[0].upper(),i])
				dataset_len+=1


#-----Shuffle Dataset------#

random.shuffle(dataset)

random.shuffle(dataset_test)

#----Activation Function-----#

def sigmod(z):
    return 1/(1+math.exp(-z))

#------d/dz of sigmod function-----#

def dsigmod_dz(z):
	return sigmod(z)*(1-sigmod(z))

#-----Learning Rate And Iteration-----#

learning=0.2
iteration=100000

#-----Training----#
print("Learning Rate = ",learning)
def train():
	#weight=[[],[],[],[],[],[],[],[]]
	weight=np.empty((len(lang),leng,26))
	for i in range(len(lang)):
		#weight[i]=np.zeros((leng,26))
		for j in range(leng):
			for k in range(26):
				weight[i][j][k]=np.random.rand()


	b=np.empty(len(lang))
	for i in range(len(lang)):
		b[i]=np.random.rand()


	for i in range(iteration):
		get=np.random.randint(len(dataset))
#		get=i
		point=dataset[get]
		target=np.zeros(len(lang))
		target[point[1]]=1
		input=np.zeros((leng,26))
		for j in range(len(point[0])):
			k=ord(point[0][j])-65
			if k >=0 and k<26:
				input[j][k]=1

		for j in range(len(lang)):
			z=b[j]
			for k in range(leng):
				for l in range(26):
					z=z+weight[j][k][l]*input[k][l]


			Pred=sigmod(z)
			error=(Pred-target[j])**2
			derror_dpred=2*(Pred-target[j])
			dPred_dz=dsigmod_dz(z)
			for k in range(leng):
				for l in range(26):
					derror_dweight=derror_dpred*dPred_dz*input[k][l]
					weight[j][k][l]-=learning*derror_dweight


			b[j]-=learning*derror_dpred*dPred_dz




	return weight,b

#print(len(lang))
#print("Training Start")
speaker.Speak("training is going to start")
calc_weight,bais=train()
#print("Training end")
speaker.Speak("training ends here")

# print(calc_weight)
# print("bais",bais)


#---Test on Known Dataset----#

def test_dataset():
	correct=0
	for i in range(len(dataset_test)):
		point=dataset_test[i]
		target=np.zeros(len(lang))
		target[point[1]]=1
		output=np.empty(len(lang))
		input=np.zeros((leng,26))
		for j in range(len(point[0])):
			k=ord(point[0][j])-65
			if k >=0 and k<26:
				input[j][k]=1 

		for j in range(len(lang)):
			z=bais[j]
			for k in range(leng):
				for l in range(26):
					z=z+calc_weight[j][k][l]*input[k][l]


			output[j]=sigmod(z)

		max_pred=output[0]
		pos=0
		for j in range(len(lang)):
			if max_pred<output[j]:
				pos=j
				max_pred=output[j]

		# print(int(point[1]))
		# print(pos)
		# print("-----")
		if pos==int(point[1]):
			correct=correct+1


	return correct


print("Test on Known Dataset")
correct=test_dataset()
accuracy=(correct*100)/len(dataset_test)
print("Accurary ",accuracy)
#speaker.Speak("Accurary "+accuracy+" percentage")

#----Test on unknown data----#

def test_unknown(point):
	#point=input("Enter String ")
	point=point.upper()
	
	output=np.empty(len(lang))
	x=np.zeros((leng,26))
	for j in range(len(point)):
		k=ord(point[j])-65
		if k >=0 and k<26:
			x[j][k]=1 



	for j in range(len(lang)):
		z=bais[j]
		for k in range(leng):
			for l in range(26):
				z=z+calc_weight[j][k][l]*x[k][l]


		output[j]=sigmod(z)


	max_pred=output[0]
	pos=0
	for j in range(len(lang)):
		if max_pred<output[j]:
			pos=j
			max_pred=output[j]


	return pos,(max_pred*100)


get=1
# while get==1:
# 	r=sr.Recognizer()
# 	with sr.Microphone() as source:
# 		print("\nSay Anything!!!")
# 		speaker.Speak("Say Anything")
# 		audio=r.listen(source,phrase_time_limit=10)
# 		print("Done !!!")
# 		speaker.Speak("Done")
# 	try:
# 		text=r.recognize_google(audio)
# 		print("Text listen are ",text)
# 		text=text.split(" ")
# 		output=np.zeros(len(lang))
# 		conf=np.zeros(len(lang))
# 		for i in range(len(text)):
# 			pos,con=test_unknown(text[i])
# 			output[pos]+=1
# 			conf[pos]+=con 

# 		max_pred=output[0]
# 		pos=0
# 		for i in range(len(lang)):
# 			if output[i]>max_pred:
# 				max_pred=output[i]
# 				pos=i


# 		print("Prediction ",lang[pos])
# 		print("Confidence ",(conf[pos]/output[pos]))
# 		#speaker.Speak(lan[pos])
# 		#speaker.Speak("Confidence "+(conf[pos]/output[pos])+" percentage")
# 		print(conf)
		
# 	except:
# 		print("Error Occured !!!")

# 	get=int(input("Enter 1 to again enter text or 0 to exit "))


		

while get==1:
	text=input("Enter String ")
	text=text.split(" ")
	output=np.zeros(len(lang))
	conf=np.zeros(len(lang))
	for i in range(len(text)):
		pos,con=test_unknown(text[i])
		output[pos]+=1
		conf[pos]+=con 

	max_pred=output[0]
	pos=0
	for i in range(len(lang)):
		if output[i]>max_pred:
			max_pred=output[i]
			pos=i


	print("Prediction ",lang[pos])
	print("Confidence ",(conf[pos]/output[pos]))
	get=int(input("Enter 1 to again enter text or 0 to exit "))













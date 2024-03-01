import speech_recognition as sp
import whisper

class VTT():
    def __init__(self,outfile):
        self.outfile=outfile
        self.r=sp.Recognizer()
        
        
    def speak(self):
        filef=open(self.outfile,"w")
        with sp.Microphone() as source:
            audio=self.r.listen(source,phrase_time_limit=5)
        ls=[]
        try:
            ls.append(self.r.recognize_whisper(audio))
        except sp.UnknownValueError:
            print("unrecognizable")
        except sp.RequestError as e:
            print("recognizer unrecognizable")
        for i in ls:
            filef.write(i)
        return ls[0]
    

#Possible use of the code    
#voiceto=VTT("transcription.txt")  
#vstring=voiceto.speak() 
#print(vstring)    

#source=sp.Microphone()



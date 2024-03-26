import speech_recognition as sp

class VTT():
    def __init__(self,outfile="outfile.txt"):
        self.outfile=outfile
        self.r=sp.Recognizer()
        
        
    def speak(self):
        filef=open(self.outfile,"w")
    
        #sp.recognizer.adjust_for_ambient_noise(source)
        with sp.Microphone() as source:
            self.r.adjust_for_ambient_noise(source=source)
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



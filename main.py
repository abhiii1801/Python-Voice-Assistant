import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import webbrowser
import pyautogui
import time
import datetime
import pyttsx3
import openai
import os

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 150)
openai.api_key = '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'

def user_feedback(result):
    print(f'\n{result}\n')
    engine.say(result)
    engine.runAndWait()

def append_to_history(user, result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join("assistant", "conversation_history.txt")  
    with open('conversation_history.txt', "a") as history_file:
        history_file.write(f"{timestamp} - User: {user}\n")
        history_file.write(f"{timestamp} - Result: {result}\n\n")

def recognition():
    user_feedback('Please show the object in front of the webcam')
       
def weather(audio):
    try:
        audio_list = audio.split()
        index_of_in = audio_list.index("in") if "in" in audio_list else -1
        if index_of_in != -1 and index_of_in < len(audio_list) - 1:
            city = " ".join(audio_list[index_of_in + 1:])
        
        user_feedback(f'Obtaining weather of {city}')
        driver = webdriver.Chrome()
        driver.minimize_window()
        
        driver.get("https://www.accuweather.com/en/in/india-weather")
        search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search your Address, City or Zip Code"]')))
        search_input.send_keys(city)

        element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.search-bar-result.search-result.source-radar')))
        element_to_click.click()

        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'temp-container')))
        temp = container.find_element(By.CLASS_NAME, 'temp').text
        phrase = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'phrase'))).text

        result = f'It feels like {phrase} with {temp} in {city}'
        append_to_history(f'weather in {city}', result)
        return result
    except Exception as e:
        error=f'Error obtaining weather: {str(e)}'
        append_to_history(f'weather in {city}', e)
        return 'error'

def open_app(audio):
    try:
        audio_list = audio.split()
        name = ' '.join(audio_list[1:])
        user_feedback(f'Opening {name}')
        
        pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.write(name)
        time.sleep(1)
        pyautogui.press('enter')
        
        result = f'Opened {name} successfully'
        user_feedback(result)
        append_to_history(f'open {name}', result)
    except Exception as e:
        error=(f"Error opening the app {e}")
        append_to_history(f'open {name}', error)
        user_feedback(error)

def play(audio):
    try:
        audio_list = audio.split()
        name = ' '.join(audio_list[1:])
        result=(f'Playing,{name} from Youtube')
        user_feedback(result)
        url=f'https://www.youtube.com/results?search_query={name}'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        video= driver.find_element(By.ID,'video-title')
        video_link = video.get_attribute("href")

        webbrowser.open(video_link,new=2)  
        append_to_history(f'play {name}', result)
    except Exception as e:
        error=(f'Error playing song {e}')  
        append_to_history(f'play {name}', error)
        user_feedback(error)

def website(audio):
    try:
        audio_list = audio.split()
        name = ' '.join(audio_list[1:-1])
        result=(f'Opening {name}')
        user_feedback(result)
        url=f'https://www.{name}.com/'
        webbrowser.open(url, new=2)
        append_to_history(f'open {name}', result)  
    except Exception as e:
        error=(f'Error opening Website {e}')
        append_to_history(f'play {name}', error)
        user_feedback(error)

def chatgpt(audio): 
    try:
        print('Fetching data from chatGPT')
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=audio,
            max_tokens=100 
        )
        generated_text = response['choices'][0]['text'].strip()
        append_to_history(audio, generated_text)
        return generated_text  
    except Exception as e:
        error=(f'Error Connecting with Chat GPT {e}') 
        append_to_history(audio, error) 

def verify(audio):
    index = audio.find('weather')
    audio_list = audio.split()
    
    if audio_list[-1].lower()=='website':
        return 'website'
    elif audio_list[0].lower()=='play':
        return 'play'
    elif audio_list[0].lower()=='open':
        return 'open'
    elif index != -1:
        return 'weather'
    elif audio == "What's this object" or audio=='what is this object':
        return 'recognition'
    else:
        return 'prompt'
      
def input_audio():
    with sr.Microphone(device_index=23) as source:
    # with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                user_feedback('Say Now')
                audio = recognizer.listen(source, timeout=10)
                print('Recognizing.....')
                text = recognizer.recognize_google(audio)
                
                if 'python' in text.lower():
                    return text
                else:
                    print("Waiting for 'python' command...")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.WaitTimeoutError:
                print("Listening timed out. No speech detected.")
            except sr.RequestError as e:
                print(f"Error connecting to Google API: {e}")
            
def commands(audio):
    if audio =='stop':
        user_feedback('Signing off !!')
        append_to_history('stop', 'stopped')
        return 'break'
    
    elif audio == 'pose' or audio=='pause':
        user_feedback('Paused')
        append_to_history('pause', 'paused')
        pyautogui.press('f10')
        
    elif audio == 'what\'s the time' or audio == 'what is the time':
        current_time = time.strftime('%I:%M %p')
        user_feedback(f'It is {current_time}')
        append_to_history('what\'s the time', current_time)
        
    elif audio.startswith('set a timer for'):
        try:
            duration = int(audio.split(' ')[-2])
            user_feedback(f'Setting a timer for {duration} seconds')

            for remaining_time in range(duration, 0, -1):
                print(f"Time remaining: {remaining_time} seconds")
                time.sleep(1)

            user_feedback('Timer completed!')
            append_to_history(audio, 'done')
        except ValueError:
            append_to_history(audio, 'Value Error')
            user_feedback('Invalid timer duration. Please specify a valid duration in seconds.')
            
    elif audio.startswith('volume'):
        try:
            volume_level = int(audio.split()[-1])
            scaled_volume = volume_level / 10.0
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(scaled_volume, None)  
            result = (f'Volume set to {volume_level}')
            user_feedback(result)
            append_to_history(audio, result)
        except Exception as e:
            append_to_history(audio,e)
            user_feedback('Please say a value between 1 and 10')
        
    else:
        return None
        
def main():
    while True:
        
        audio =input_audio()
        # audio ="python what's the weather in Chandigarh"
        if audio.lower().startswith('python '):
            audio = audio[len('python '):]
            command = commands(audio)
            if command == 'break':
                break
            
            not_words = ['stop', 'pose', 'pause','volume',"what's the time",'set a timer for','what is the time']
            
            if not any(word in audio for word in not_words):
                print(f'Your prompt is "{audio}"\n')
                verification =verify(audio)
            
                if verification == 'prompt':
                    answer = chatgpt(audio)
                    user_feedback(answer)
                    
                elif verification == 'website':
                    website(audio)
                    
                elif verification == 'play':
                    play(audio)
                
                elif verification == 'open':
                    open_app(audio)    
                    
                elif verification == 'weather':
                    result = weather(audio)
                    user_feedback(result)
                
                elif verification == 'recognition':
                    recognition()
                    
                else:
                    break
        else:
            print('Invalid Input')
 
if __name__ == "__main__":
    main()


import os, sys

def setControllerAction():
    return {
                61478 : 'Keyboard Up Arrow',
                61480 : 'Keyboard Down Arrow',
                61479 : 'Keyboard Right Arrow',
                61448 : 'Keyboard Backspace Button',
                61533 : 'Keyboard Menu Button',
                61467 : 'Keyboard ESC Button',
                    216 : 'Remote Back Button',
                    247 : 'Remote Menu Button',
                    229 : 'Remote Title',
                    207 : 'Remote 0',
                    166 : 'Remote Up',
                    167 : 'Remote Down',
                    168 : 'Remote Right',
                    256 : 'A Button',
                    257 : 'B Button',
                    258 : 'X Button',
                    259 : 'Y Button',
                    260 : 'Black Button',
                    261 : 'White Button',
                    274 : 'Start Button',
                    275 : 'Back Button',
                    270 : 'DPad Up',
                    271 : 'DPad Down',
                    272 : 'DPad Left',
                    273 : 'DPad Right'
                }

def getpresetservers():
    return {
            "gmail.com" : ["pop.gmail.com","smtp.gmail.com","995","587","0"],
            "ihug.co.nz" : ["pop.ihug.co.nz","smtp.ihug.co.nz","0","0","5"],
            "xtra.co.nz" : ["pop3.xtra.co.nz","smtp.xtra.co.nz","0","0","100"],
            "sky.com" : ["pop.sky.com","smtp.sky.com","0","0","200"],
            "aol.com" : ["pop.aol.com","smtp.aol.com","0","587","5000"],
            "aim.com" : ["pop.aim.com","smtp.aim.com","0","587","5000"],
            "earthlink.net" : ["pop.earthlink.net","smtpauth.earthlink.net","0","587","100"],
            }

def getfiletypes(image=False,audio=False,video=False,text=False):
    if image: return ["jpg","jpeg","gif","png","bmp"]
    if audio: return ["wav","mp3","mpa","mp2","ac3","dts"]
    if video: return ["avi","wmv","mpg"]
    if text: return ["txt", "doc", "rtf", "xml", "bat"]
    

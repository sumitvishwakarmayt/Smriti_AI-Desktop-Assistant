import webbrowser
import os
import subprocess
import platform


class AppLauncher:
    def __init__(self):
        self.system = platform.system()  # Windows, Linux, or Darwin (macOS)
        
    def open_website(self, url):
        """Open a website in default browser"""
        try:
            webbrowser.open(url)
            return f"Opening {url} in your web browser"
        except Exception as e:
            return f"Sorry, I couldn't open {url}: {str(e)}"
    
    def open_application(self, app_name):
        """Open desktop applications"""
        app_name = app_name.lower()
        
        # Web browsers
        if "chrome" in app_name:
            return self.open_browser("chrome")
        elif "firefox" in app_name or "mozilla" in app_name:
            return self.open_browser("firefox")
        elif "edge" in app_name:
            return self.open_browser("edge")
        elif "browser" in app_name or "web" in app_name:
            return self.open_browser("default")
        
        # Common applications
        elif "notepad" in app_name:
            return self.open_notepad()
        elif "calculator" in app_name:
            return self.open_calculator()
        elif "file explorer" in app_name or "explorer" in app_name:
            return self.open_file_explorer()
        elif "command" in app_name or "cmd" in app_name or "terminal" in app_name:
            return self.open_command_prompt()
        elif "vs code" in app_name or "code" in app_name:
            return self.open_vscode()
        
        else:
            return f"Sorry, I don't know how to open {app_name}"

    def close_application(self, app_name):
        """Close desktop applications by process name patterns"""
        try:
            name = app_name.lower()
            if self.system == "Windows":
                # Map friendly names to process image names
                name_map = {
                    "notepad": ["notepad.exe"],
                    "calculator": ["Calculator.exe", "CalculatorApp.exe", "ApplicationFrameHost.exe"],
                    "chrome": ["chrome.exe"],
                    "firefox": ["firefox.exe"],
                    "edge": ["msedge.exe"],
                    "code": ["Code.exe"],
                    "vs code": ["Code.exe"],
                    "command prompt": ["cmd.exe"],
                    "terminal": ["WindowsTerminal.exe", "cmd.exe", "powershell.exe", "pwsh.exe"],
                }
                targets = None
                for key, procs in name_map.items():
                    if key in name:
                        targets = procs
                        break
                # If not a known key, try to form an exe name
                if targets is None:
                    guessed = name.replace(" ", "") + ".exe"
                    targets = [guessed]

                success = False
                for proc in targets:
                    try:
                        subprocess.run(["taskkill", "/IM", proc, "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        success = True
                    except Exception:
                        pass
                if success:
                    return f"Closing {app_name}"
                return f"I couldn't find {app_name} running"
            else:
                # macOS and Linux: best-effort pkill
                pattern_map = {
                    "notepad": ["TextEdit", "gedit"],
                    "calculator": ["Calculator", "gnome-calculator"],
                    "chrome": ["Google Chrome", "chrome"],
                    "firefox": ["firefox"],
                    "edge": ["Microsoft Edge", "microsoft-edge"],
                    "code": ["Visual Studio Code", "code"],
                    "terminal": ["Terminal", "gnome-terminal"],
                }
                targets = None
                for key, pats in pattern_map.items():
                    if key in name:
                        targets = pats
                        break
                if targets is None:
                    targets = [name]
                success = False
                for pat in targets:
                    try:
                        subprocess.run(["pkill", "-f", pat])
                        success = True
                    except Exception:
                        pass
                if success:
                    return f"Closing {app_name}"
                return f"I couldn't find {app_name} running"
        except Exception as e:
            return f"Sorry, I couldn't close {app_name}: {str(e)}"

    def open_browser(self, browser_type):
        """Open specific browser"""
        try:
            if browser_type == "chrome":
                webbrowser.get("chrome").open("https://www.google.com")
                return "Opening Google Chrome"
            elif browser_type == "firefox":
                webbrowser.get("firefox").open("https://www.google.com")
                return "Opening Mozilla Firefox"
            elif browser_type == "edge":
                webbrowser.get("edge").open("https://www.google.com")
                return "Opening Microsoft Edge"
            else:
                webbrowser.open("https://www.google.com")
                return "Opening your default web browser"
        except Exception as e:
            return f"Sorry, I couldn't open the browser: {str(e)}"

    def open_notepad(self):
        """Open Notepad"""
        try:
            if self.system == "Windows":
                os.system("notepad")
                return "Opening Notepad"
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "TextEdit"])
                return "Opening TextEdit"
            else:  # Linux
                subprocess.run(["gedit"])
                return "Opening text editor"
        except Exception as e:
            return f"Sorry, I couldn't open Notepad: {str(e)}"

    def open_calculator(self):
        """Open Calculator"""
        try:
            if self.system == "Windows":
                os.system("calc")
                return "Opening Calculator"
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Calculator"])
                return "Opening Calculator"
            else:  # Linux
                subprocess.run(["gnome-calculator"])
                return "Opening Calculator"
        except Exception as e:
            return f"Sorry, I couldn't open Calculator: {str(e)}"

    def open_file_explorer(self):
        """Open File Explorer"""
        try:
            if self.system == "Windows":
                os.system("explorer")
                return "Opening File Explorer"
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Finder"])
                return "Opening Finder"
            else:  # Linux
                subprocess.run(["nautilus"])
                return "Opening File Manager"
        except Exception as e:
            return f"Sorry, I couldn't open File Explorer: {str(e)}"

    def open_command_prompt(self):
        """Open Command Prompt/Terminal"""
        try:
            if self.system == "Windows":
                os.system("cmd")
                return "Opening Command Prompt"
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Terminal"])
                return "Opening Terminal"
            else:  # Linux
                subprocess.run(["gnome-terminal"])
                return "Opening Terminal"
        except Exception as e:
            return f"Sorry, I couldn't open Command Prompt: {str(e)}"

    def open_vscode(self):
        """Open Visual Studio Code"""
        try:
            if self.system == "Windows":
                os.system("code")
                return "Opening Visual Studio Code"
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Visual Studio Code"])
                return "Opening Visual Studio Code"
            else:  # Linux
                subprocess.run(["code"])
                return "Opening Visual Studio Code"
        except Exception as e:
            return f"Sorry, I couldn't open Visual Studio Code: {str(e)}"

    def open_specific_website(self, site_name):
        """Open specific websites by name"""
        sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "github": "https://www.github.com",
            "linkedin": "https://www.linkedin.com",
            "whatsapp": "https://web.whatsapp.com",
            "gmail": "https://mail.google.com",
            "drive": "https://drive.google.com",
            "maps": "https://maps.google.com",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "prime": "https://www.primevideo.com",
            "hotstar": "https://www.hotstar.com"
        }
        
        site_name = site_name.lower()
        for key, url in sites.items():
            if key in site_name:
                return self.open_website(url)
        
        return f"Sorry, I don't know how to open {site_name}"


# Global instance
_app_launcher = AppLauncher()

def open_application(app_name):
    return _app_launcher.open_application(app_name)

def open_website(url_or_name):
    # Check if it's a URL or website name
    if url_or_name.startswith(('http://', 'https://', 'www.')):
        return _app_launcher.open_website(url_or_name)
    else:
        return _app_launcher.open_specific_website(url_or_name)

def close_application(app_name):
    return _app_launcher.close_application(app_name)
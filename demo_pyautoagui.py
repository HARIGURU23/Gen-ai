import time
import pyautogui
import pyperclip

# Safety options
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.25

def main():
    contact_name = "sonali"
    message_text = "An automatic love note straight from Ms. Azaghis heart"


    print("Starting in 3 seconds... Move mouse to top-left corner to cancel.")
    time.sleep(3)

    # 1️⃣ Press Windows key to open search
    pyautogui.press('win')
    time.sleep(0.8)

    # 2️⃣ Type "whatsapp" and open it
    pyautogui.typewrite('whatsapp', interval=0.05)
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(3)  # wait for WhatsApp to load

    # 3️⃣ Open WhatsApp search (Ctrl + F)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.3)

    # 4️⃣ Type the contact name ("karthiapk")
    pyperclip.copy(contact_name)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)

    # 5️⃣ Wait 5 seconds for search results
    time.sleep(5)

    # 6️⃣ Move down once and wait 2 seconds
    pyautogui.press('down')
    time.sleep(2)

    # 7️⃣ Open the chat
    pyautogui.press('enter')
    time.sleep(1)

    # 8️⃣ Type and send the message
    pyperclip.copy(message_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')

    print("✅ Message sent successfully!")

if __name__ == "__main__":
    main()

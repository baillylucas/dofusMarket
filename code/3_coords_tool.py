import pygame
import sys
from pynput import mouse, keyboard
import pyautogui
import win32gui
import win32con
import win32api

class ScreenRectangleSelector:
    def __init__(self):
        pygame.init()
        
        # Obtenir la taille de l'écran
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Création de la fenêtre transparente
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        
        # Rendre la fenêtre semi-transparente et cliquable
        hwnd = pygame.display.get_wm_info()['window']
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                             win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                             win32con.WS_EX_LAYERED | 
                             win32con.WS_EX_TRANSPARENT)
        # Définir la transparence pour voir les éléments
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 64, win32con.LWA_ALPHA)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        self.clicks = []
        self.rectangle_validated = False
        self.running = True
        
        # Surface pour le dessin
        self.transparent_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)

    def reset_state(self):
        self.clicks = []
        self.rectangle_validated = False
        self.transparent_surface.fill((0,0,0,0))
        self.draw()

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            if self.rectangle_validated:
                self.reset_state()
            elif len(self.clicks) >= 2:
                self.reset_state()
            
            self.clicks.append((x, y))
            self.draw()

    def on_press(self, key):
        if key == keyboard.Key.enter and len(self.clicks) == 2:
            self.rectangle_validated = True
            x1, y1 = self.clicks[0]
            x2, y2 = self.clicks[1]
            print(f"\nCoordonnées du rectangle validé:")
            print(f"Coin supérieur gauche: ({min(x1, x2)}, {min(y1, y2)})")
            print(f"Coin inférieur droit: ({max(x1, x2)}, {max(y1, y2)})")
            self.draw()
        elif key == keyboard.Key.esc:
            self.running = False
            return False

    def draw(self):
        # Effacer l'écran avec transparence totale
        self.screen.fill((0,0,0))
        self.transparent_surface.fill((0,0,0,0))
        
        # Dessiner les points en rouge
        for x, y in self.clicks:
            pygame.draw.circle(self.transparent_surface, (255, 0, 0, 255), (x, y), 5)
        
        if len(self.clicks) == 2:
            x1, y1 = self.clicks[0]
            x2, y2 = self.clicks[1]
            
            # Couleurs pour le rectangle
            if self.rectangle_validated:
                fill_color = (0, 255, 0, 64)  # Vert transparent pour le remplissage
                border_color = (0, 255, 0, 255)  # Vert opaque pour la bordure
            else:
                fill_color = (0, 0, 255, 64)  # Bleu transparent pour le remplissage
                border_color = (0, 0, 255, 255)  # Bleu opaque pour la bordure
            
            rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))
            
            # Dessiner d'abord le remplissage
            pygame.draw.rect(self.transparent_surface, fill_color, rect)
            # Puis dessiner la bordure
            pygame.draw.rect(self.transparent_surface, border_color, rect, 2)
        
        self.screen.blit(self.transparent_surface, (0,0))
        pygame.display.flip()

    def run(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        print("Cliquez pour placer les points du rectangle.")
        print("Appuyez sur Entrée pour valider le rectangle.")
        print("Appuyez sur Échap pour quitter.")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.time.wait(10)
        
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        pygame.quit()

if __name__ == "__main__":
    selector = ScreenRectangleSelector()
    selector.run()
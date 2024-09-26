import pygame
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image


class QRGenerator:
    def __init__(self, box_size=10, border=4, fill_color="black",
                 back_color="white"):
        self.box_size = box_size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color

    def generate_qr_surface(self, data, size=(300, 300)):
        # Crear el objeto QR
        qr = qrcode.QRCode(version=1, box_size=self.box_size,
                           border=self.border)
        qr.add_data(data)
        qr.make(fit=True)

        # Crear una imagen del código QR con esquinas redondeadas
        qr_image = qr.make_image(
            fill_color=self.fill_color,
            back_color=self.back_color,
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )

        # Redimensionar la imagen si es necesario
        qr_image = qr_image.resize(size, Image.LANCZOS)

        # Convertir la imagen PIL a una superficie de Pygame
        mode = qr_image.mode
        size = qr_image.size
        data = qr_image.tobytes()
        return pygame.image.fromstring(data, size, mode)


# Ejemplo de uso
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("QR Code Example")

    qr_gen = QRGenerator()
    qr_surface = qr_gen.generate_qr_surface("https://www.ejemplo.com",
                                            (300, 300))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        screen.blit(qr_surface, (50, 50))  # Centrar el QR en la pantalla
        pygame.display.flip()

    pygame.quit()

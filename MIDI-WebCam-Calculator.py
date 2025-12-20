import cv2
import mediapipe as mp
import time
import tkinter as tk
import random
import threading
from mido import MidiFile, MidiTrack, Message

# ------------------ MEDIA PIPE ------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

hand_start_time = None
HAND_SECONDS = 10
calculator_opened = False

def detect_hands():
    global hand_start_time, calculator_opened

    print("Muestra tus manos durante 10 segundos...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            if hand_start_time is None:
                hand_start_time = time.time()

            elapsed = int(time.time() - hand_start_time)

            cv2.putText(frame, f"Tiempo: {elapsed}/10",
                        (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

            if elapsed >= HAND_SECONDS:
                calculator_opened = True
                break
        else:
            hand_start_time = None

        cv2.imshow("Camara - Deteccion de Manos", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def abrir_calculadora():
    def agregar(num):
        entrada.set(entrada.get() + str(num))

    def limpiar():
        entrada.set("")

    def calcular():
        try:
            if "+" in entrada.get():
                crear_midi()
            entrada.set(str(eval(entrada.get())))
        except:
            entrada.set("Error")

    def crear_midi():
        midi = MidiFile()
        track = MidiTrack()
        midi.tracks.append(track)
        track.append(Message('program_change', program=0))

        # Definir las notas base
        notas = [60, 62, 64, 65, 67, 69, 71, 72]  # Notas en la octava central de piano

        # Generar intervalos de tercera menor y séptima mayor
        tercera_menor = [3, 6, 9, 12, 15, 18]  # Terceras menores en semitonos
        septima_mayor = [11, 14, 17, 20, 23]  # Séptimas mayores en semitonos

        # Duración de las notas (en ticks)
        duraciones_posibles = [480, 960, 720]  # Variación en la duración de las notas (en ticks)
        
        # Generar 30 intervalos de tercera menor
        for _ in range(30):
            nota_base = random.choice(notas)
            intervalo_tercera_menor = random.choice(tercera_menor)
            nota_destino = nota_base + intervalo_tercera_menor
            duracion = random.choice(duraciones_posibles)  # Duración aleatoria
            track.append(Message('note_on', note=nota_base, velocity=64, time=0))
            track.append(Message('note_off', note=nota_base, velocity=64, time=duracion))
            track.append(Message('note_on', note=nota_destino, velocity=64, time=0))
            track.append(Message('note_off', note=nota_destino, velocity=64, time=duracion))

        # Generar 40 intervalos de séptima mayor
        for _ in range(40):
            nota_base = random.choice(notas)
            intervalo_septima_mayor = random.choice(septima_mayor)
            nota_destino = nota_base + intervalo_septima_mayor
            duracion = random.choice(duraciones_posibles)  # Duración aleatoria
            track.append(Message('note_on', note=nota_base, velocity=64, time=0))
            track.append(Message('note_off', note=nota_base, velocity=64, time=duracion))
            track.append(Message('note_on', note=nota_destino, velocity=64, time=0))
            track.append(Message('note_off', note=nota_destino, velocity=64, time=duracion))

        # Asegurarse de que el archivo MIDI dure al menos 7 minutos
        # 7 minutos = 7 * 60 segundos = 420 segundos
        total_ticks = 420 * 480  # 420 segundos * 480 ticks por segundo
        total_time = sum(msg.time for msg in track)

        if total_time < total_ticks:
            # Si no hemos alcanzado los 7 minutos, agregar notas extra con duraciones cortas
            while total_time < total_ticks:
                track.append(Message('note_on', note=random.choice(notas), velocity=64, time=0))
                track.append(Message('note_off', note=random.choice(notas), velocity=64, time=random.choice(duraciones_posibles)))
                total_time += random.choice(duraciones_posibles)

        midi.save("resultado_midi.mid")
        print("🎵 MIDI generado")

    # -------- TKINTER --------
    root = tk.Tk()
    root.title("Calculadora MIDI")
    root.geometry("300x400")
    root.config(bg="#333333")

    entrada = tk.StringVar()
    display = tk.Entry(root, textvariable=entrada, font=("Arial", 24), bd=10, relief="sunken", justify="right", bg="black", fg="#00FF00")
    display.grid(row=0, column=0, columnspan=4)

    botones = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
        ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3),
        ('C', 5, 0)
    ]

    # Colocar los botones con los colores
    for (texto, fila, columna) in botones:
        if texto == 'C':
            boton = tk.Button(root, text=texto, font=("Arial", 18), width=5, height=2, command=limpiar, bg="#333333", fg="white", relief="raised")
        elif texto == '=':
            boton = tk.Button(root, text=texto, font=("Arial", 18), width=5, height=2, command=calcular, bg="#333333", fg="white", relief="raised")
        else:
            boton = tk.Button(root, text=texto, font=("Arial", 18), width=5, height=2, command=lambda t=texto: agregar(t), bg="#333333", fg="white", relief="raised")
        
        boton.grid(row=fila, column=columna)

    root.mainloop()

# -------------------- MAIN --------------------
def main():
    # Thread para la detección de manos
    hands_thread = threading.Thread(target=detect_hands)
    hands_thread.start()

    # Espera hasta que las manos se detecten durante 10 segundos
    while not calculator_opened:
        time.sleep(1)

    # Una vez que las manos se detecten durante 10 segundos, abrir la calculadora
    if calculator_opened:
        print("Manos detectadas durante 10 segundos. Abriendo la calculadora...")
        abrir_calculadora()

if __name__ == "__main__":
    main()

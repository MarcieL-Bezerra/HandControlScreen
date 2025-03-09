import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Inicializar o Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Inicializar o drawing
mp_drawing = mp.solutions.drawing_utils

# Variáveis para controlar o clique
mouse_down = False
last_finger_state = None

while cap.isOpened():
    # Capturar a imagem da webcam
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Converter a imagem para RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # Processar a imagem com o Hands
    results = hands.process(image)

    # Capturar a imagem da área de trabalho
    desktop_image = pyautogui.screenshot()

    # Converter a imagem da área de trabalho para numpy array
    desktop_image = np.array(desktop_image)

    # Função para identificar a mão fechada
    def mao_fechada(results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Verificar se a mão está fechada
                if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y:
                    print("Mão fechada ")
                    pyautogui.mouseDown(button='left')

    # Função para identificar a mão aberta
    def mao_aberta(results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Verificar se a mão está aberta
                if (hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
                    hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
                    hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y and
                    hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y):
                    print("Mão aberta")
                    pyautogui.mouseUp(button='left')     

    # Superpor a imagem da mão detectada sobre a imagem da área de trabalho
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # mp_drawing.draw_landmarks(desktop_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(desktop_image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(128, 128, 128), thickness=5, circle_radius=5),  # Círculos
                             mp_drawing.DrawingSpec(color=(128, 128, 128), thickness=10, circle_radius=5))  # Linhas

            # Verificar se a mão é a direita
            if handedness.classification[0].label == 'Right':
                # Obter a posição do dedo indicador
                x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

                # Converter a posição para coordenadas de tela
                screen_width, screen_height = pyautogui.size()
                mouse_x = int(x * screen_width)
                mouse_y = int(y * screen_height)

                # Mover o mouse para a posição do dedo indicador
                pyautogui.moveTo(mouse_x, mouse_y)

                # Verificar se a mão está fechada e não estava fechada anteriormente
                mao_fechada(results)
                mao_aberta(results)
                
    # Exibir a imagem
    cv2.imshow('MediaPipe Hands', desktop_image)

    # Sair com a tecla 'q'
    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
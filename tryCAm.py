import cv2

# Функция для поиска доступных камер
def list_cameras():
    available_cameras = []
    for index in range(10):  # Проверяем первые 10 индексов
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

# Поиск доступных камер
cameras = list_cameras()
if cameras:
    print(f"Доступные камеры: {cameras}")
else:
    print("Камеры не найдены.")

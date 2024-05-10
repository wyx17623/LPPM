import cv2
from ultralytics import YOLO

if __name__ == '__main__':
    # Load the classification model
    classify_model = YOLO('classifyBest.pt')
    # Load the detection model
    detect_model = YOLO('detectBest.pt')

    # Read the input image
    source = cv2.imread('0b10bacd-eb17-4f5d-88f3-32c32c5c27a1.jpg')

    # Perform image classification
    classify_results = classify_model(source)

    # Iterate over each image's classification result
    for classify_result in classify_results:
        # Get the first prediction
        first_prediction = classify_result.names[classify_result.probs.top1]

        # Display the first prediction at the top left corner with a large font size and moved downwards
        cv2.putText(source, first_prediction, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 0, 255), 6)
        break  # Stop after processing the first image's result

    # Save the processed image
    cv2.imwrite('processed_image.jpg', source)

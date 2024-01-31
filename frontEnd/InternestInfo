<?php
// Read the JSON data sent from the client
$data = json_decode(file_get_contents('php://input'), true);

// Check if the 'interests' key exists in the data
if (isset($data['interests'])) {
    // Save the interests to a file or database (replace this with your actual saving logic)
    $file = 'user_interests.txt';
    file_put_contents($file, $data['interests'] . PHP_EOL, FILE_APPEND);

    // Send a response back to the client
    echo json_encode(['status' => 'success']);
} else {
    // If 'interests' key is not present in the data
    echo json_encode(['status' => 'error', 'message' => 'Invalid data']);
}
?>

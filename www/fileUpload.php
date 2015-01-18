
<?php
echo $_FILES['image']['name'] . '<br/>';

$target_path = "files/";

$target_path = $target_path . basename($_FILES['image']['name']);

try {
    if (!move_uploaded_file($_FILES['image']['tmp_name'], $target_path)) {
        throw new Exception('Could not move file');
    }

    exec('python /root/jsonparsersimple.py');

} catch (Exception $e) {
    die('An error occurred:' . $e->getMessage());
}
?>

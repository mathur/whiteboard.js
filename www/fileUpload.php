
<?php
echo $_FILES['image']['name'] . '<br/>';

$target_path = "files/";

$command = "python /root/jsonparser.py";

$target_path = $target_path . basename($_FILES['image']['name']);

try {
    if (!move_uploaded_file($_FILES['image']['tmp_name'], $target_path)) {
        throw new Exception('Could not move file');
    }

    echo "The file " . basename($_FILES['image']['name']) .
    " has been uploaded";

    string exec ( string $command [, array &$output [, int &$return_var ]] )

} catch (Exception $e) {
    die('File did not upload: ' . $e->getMessage());
}
?>

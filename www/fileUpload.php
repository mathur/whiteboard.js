
<?php
echo $_FILES['image']['name'] . '<br/>';

$target_path = "files/";
$current_time = time();

$target_path = $target_path . basename($_FILES['image']['name']);

try {
    if (!move_uploaded_file($_FILES['image']['tmp_name'], $target_path)) {
        throw new Exception('Could not move file');
    }

    echo "The file " . basename($_FILES['image']['name']) .
    " has been uploaded";

    $command = escapeshellcmd('python /root/test.py ' . $current_time);
	$output = shell_exec($command);

	throw new Exception($current_time);

} catch (Exception $e) {
    die('' . $e->getMessage());
}
?>